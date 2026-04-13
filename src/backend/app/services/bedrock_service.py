"""Bedrock Agents Runtime invocation service."""
import json
import logging
import re
from pathlib import Path
from typing import Any, cast

import boto3

from app.config import settings

logger = logging.getLogger(__name__)

FIXTURES_DIR = Path(__file__).parents[4] / "fixtures"

# DEMO_MODE fixture routing patterns (matched against prompt text)
_DEMO_ROUTES = [
    (re.compile(r"anomal", re.I), "sample-anomaly.json"),
    (re.compile(r"recommend|saving|rightsize|idle", re.I), "sample-recommendations.json"),
    (re.compile(r"cost|spend|budget|forecast|variance", re.I), "sample-cost-data.json"),
]


def _demo_response(prompt: str) -> dict[str, Any]:
    """Return fixture data matched to prompt keywords."""
    for pattern, filename in _DEMO_ROUTES:
        if pattern.search(prompt):
            fixture_path = FIXTURES_DIR / filename
            if fixture_path.exists():
                data = cast(dict[str, Any], json.loads(fixture_path.read_text()))
                data["demo_mode"] = True
                return data
    return {"message": "Demo mode active. No matching fixture.", "demo_mode": True}


async def invoke_agent(
    session_id: str,
    prompt: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Invoke Bedrock Agents Runtime and stream response chunks.

    Returns the completed agent response as a dict with a 'response' key.
    Falls back to fixture data when DEMO_MODE=true.
    """
    if settings.demo_mode:
        return _demo_response(prompt)

    if not settings.bedrock_agent_id:
        logger.warning("BEDROCK_AGENT_ID not configured")
        return {"error": "Bedrock agent not configured", "response": ""}

    client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)
    session_attributes: dict[str, str] = {}
    if context:
        session_attributes = {k: str(v) for k, v in context.items()}


    try:
        result = client.invoke_agent(
            agentId=settings.bedrock_agent_id,
            agentAliasId=settings.bedrock_agent_alias_id,
            sessionId=session_id,
            inputText=prompt,
            sessionState={"sessionAttributes": session_attributes},
        )

        full_response = ""
        for event in result.get("completion", []):
            chunk = event.get("chunk", {})
            if "bytes" in chunk:
                full_response += chunk["bytes"].decode("utf-8")

        return {"response": full_response, "session_id": session_id}

    except client.exceptions.ResourceNotFoundException as exc:
        logger.error(json.dumps({"error": "agent_not_found", "detail": str(exc)}))
        return {"error": "Agent not found", "response": ""}
    except Exception as exc:  # noqa: BLE001
        logger.error(json.dumps({"error": "bedrock_invocation_failed", "detail": str(exc)}))
        return {"error": "Bedrock invocation failed", "response": ""}
