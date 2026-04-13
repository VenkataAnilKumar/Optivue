"""Jira ticket creation adapter."""
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

import boto3
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _get_jira_credentials() -> tuple[str, str, str]:
    """Fetch Jira URL + token from Secrets Manager."""
    if settings.demo_mode:
        return "https://demo.atlassian.net", "demo-token", "FINOPS"
    sm = boto3.client("secretsmanager", region_name=settings.aws_region)
    secret = json.loads(
        sm.get_secret_value(SecretId="finops/jira-api-token")["SecretString"]
    )
    return secret["jira_base_url"], secret["jira_api_token"], secret.get("jira_project_key", "FINOPS")


async def create_jira_ticket(
    recommendation_id: str,
    approval_token: str,
    actor: str,
    title: str = "",
    description: str = "",
    action_type: str = "rightsizing",
) -> dict[str, Any]:
    """Create a Jira ticket for a finops action and record it in action-history.

    Called only AFTER approval_token has been validated.
    """
    jira_base_url, jira_api_token, project_key = _get_jira_credentials()

    ticket_summary = title or f"[FinOps] {action_type.replace('_', ' ').title()} — {recommendation_id[:8]}"
    ticket_description = description or (
        f"Recommendation ID: {recommendation_id}\nApproval Token: {approval_token[:8]}...\n"
        f"Requested by: {actor}\nAction type: {action_type}"
    )

    if settings.demo_mode:
        demo_ticket_id = f"FINOPS-{uuid.uuid4().hex[:4].upper()}"
        ticket_url = f"{jira_base_url}/browse/{demo_ticket_id}"
        logger.info(json.dumps({"event": "demo_ticket_created", "ticket_id": demo_ticket_id}))
        result = {
            "ticket_id": demo_ticket_id,
            "ticket_url": ticket_url,
            "status": "created",
            "demo_mode": True,
        }
    else:
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": ticket_summary,
                "description": {
                    "version": 1,
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": ticket_description}],
                        }
                    ],
                },
                "issuetype": {"name": "Task"},
                "labels": ["finops", action_type],
            }
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{jira_base_url}/rest/api/3/issue",
                json=payload,
                headers={
                    "Authorization": f"Bearer {jira_api_token}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        ticket_id = data.get("key", "")
        ticket_url = f"{jira_base_url}/browse/{ticket_id}"
        result = {"ticket_id": ticket_id, "ticket_url": ticket_url, "status": "created"}

    # Append to action-history (PutItem only — append-only)
    dynamo = boto3.resource("dynamodb", region_name=settings.aws_region)
    table = dynamo.Table(settings.action_history_table_name)
    table.put_item(Item={
        "pk": f"ACTION#{recommendation_id}",
        "sk": f"HISTORY#{datetime.now(UTC).isoformat()}",
        "event_type": "ticket_created",
        "recommendation_id": recommendation_id,
        "ticket_id": result["ticket_id"],
        "ticket_url": result["ticket_url"],
        "actor": actor,
        "action_type": action_type,
        "approval_token": approval_token[:8] + "...",  # truncated for security
        "created_at": datetime.now(UTC).isoformat(),
    })

    return result
