"""Bedrock action group handler: evaluate_action_risk."""
import json
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

_NO_DELETION_PREFIXES = ("prod", "production", "prd")


def _is_production_resource(resource_id: str, environment: str) -> bool:
    return environment == "prod" or any(
        resource_id.lower().startswith(p) for p in _NO_DELETION_PREFIXES
    )


def evaluate_risk(action_type: str, resource_id: str, environment: str) -> dict[str, Any]:
    """Evaluate risk for a proposed action.

    Returns a risk assessment dict including whether the action is policy_blocked.
    Rule: no autonomous deletion of production resources.
    """
    policy_blocked = False
    block_reason = None

    if action_type == "delete" and _is_production_resource(resource_id, environment):
        policy_blocked = True
        block_reason = "Autonomous deletion of production resources is strictly prohibited."
        logger.error(json.dumps({
            "event": "policy_blocked",
            "action_type": action_type,
            "resource_id": resource_id,
            "environment": environment,
        }))

    risk_level = "high" if environment == "prod" else "medium" if environment == "staging" else "low"
    requires_dual_approval = environment == "prod" and action_type in (
        "rightsizing",
        "commitment_purchase",
    )

    return {
        "action_type": action_type,
        "resource_id": resource_id,
        "environment": environment,
        "risk_level": risk_level,
        "policy_blocked": policy_blocked,
        "block_reason": block_reason,
        "requires_dual_approval": requires_dual_approval,
        "evaluated_at": datetime.now(UTC).isoformat(),
    }


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Bedrock action group handler for evaluate_action_risk."""
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    action_type = params.get("action_type", "unknown")
    resource_id = params.get("resource_id", "")
    environment = params.get("environment", "prod")

    result = evaluate_risk(action_type, resource_id, environment)

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event["actionGroup"],
            "function": event["function"],
            "functionResponse": {
                "responseBody": {
                    "TEXT": {"body": json.dumps(result)}
                }
            },
        },
    }
