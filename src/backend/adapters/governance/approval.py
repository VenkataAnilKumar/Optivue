"""Approval token lifecycle: request, status, validate."""
import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

import boto3

from app.config import settings

logger = logging.getLogger(__name__)

_TOKEN_TTL_HOURS = 4

# Approval matrix - environment/action_type → required approver roles
_APPROVAL_MATRIX: dict[str, dict[str, list[str]]] = {
    "prod": {
        "rightsizing": ["engineering-manager", "finops-analyst"],
        "idle_shutdown": ["engineering-manager"],
        "commitment_purchase": ["finops-analyst", "finance"],
        "default": ["engineering-manager", "finops-analyst"],
    },
    "staging": {
        "default": ["finops-analyst"],
    },
    "dev": {
        "default": [],  # auto-approved for low-risk
    },
}


def _table():
    dynamo = boto3.resource("dynamodb", region_name=settings.aws_region)
    return dynamo.Table(settings.approvals_table_name)


def _required_approvers(environment: str, action_type: str) -> list[str]:
    env_matrix = _APPROVAL_MATRIX.get(environment, _APPROVAL_MATRIX["prod"])
    return env_matrix.get(action_type, env_matrix.get("default", ["finops-analyst"]))


async def request_approval(
    recommendation_id: str,
    action_type: str,
    requester: str,
    environment: str = "prod",
) -> dict[str, Any]:
    """Create an approval request record."""
    approval_request_id = str(uuid.uuid4())
    approval_token = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=_TOKEN_TTL_HOURS)
    ttl_epoch = int(expires_at.timestamp())

    required_approvers = _required_approvers(environment, action_type)

    item = {
        "pk": f"APPROVAL#{approval_request_id}",
        "sk": "METADATA",
        "approval_request_id": approval_request_id,
        "approval_token": approval_token,
        "recommendation_id": recommendation_id,
        "action_type": action_type,
        "requester": requester,
        "environment": environment,
        "required_approvers": required_approvers,
        "approvals_received": [],
        "status": "pending",
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "ttl": ttl_epoch,
    }
    _table().put_item(Item=item)
    logger.info(json.dumps({
        "event": "approval_requested",
        "approval_request_id": approval_request_id,
        "recommendation_id": recommendation_id,
        "action_type": action_type,
    }))
    return {
        "approval_request_id": approval_request_id,
        "approval_token": approval_token,
        "status": "pending",
        "required_approvers": required_approvers,
        "expires_at": expires_at.isoformat(),
    }


async def get_approval_status(approval_request_id: str) -> dict[str, Any]:
    """Return the current approval record."""
    resp = _table().get_item(Key={"pk": f"APPROVAL#{approval_request_id}", "sk": "METADATA"})
    item = resp.get("Item")
    if not item:
        return {"error": "approval_not_found", "approval_request_id": approval_request_id}
    return {
        "approval_request_id": item["approval_request_id"],
        "approval_token": item["approval_token"],
        "recommendation_id": item["recommendation_id"],
        "status": item["status"],
        "required_approvers": item.get("required_approvers", []),
        "approvals_received": item.get("approvals_received", []),
        "expires_at": item["expires_at"],
    }


async def validate_approval_token(
    approval_token: str,
    recommendation_id: str,
    actor_role: str,
) -> bool:
    """Validate token: must be pending, not expired, and actor role permitted.

    Non-negotiable: this check executes FIRST before any mutating action.
    """
    table = _table()
    # Query by token using GSI (by-status-index covers pk prefix APPROVAL#)
    # Fallback: scan with filter (demo/test environments only)
    try:
        resp = table.scan(
            FilterExpression=(
                boto3.dynamodb.conditions.Attr("approval_token").eq(approval_token)
                & boto3.dynamodb.conditions.Attr("recommendation_id").eq(recommendation_id)
            )
        )
        items = resp.get("Items", [])
        if not items:
            logger.warning(json.dumps({"event": "approval_token_not_found", "token": approval_token[:8]}))
            return False

        item = items[0]

        if item["status"] != "pending":
            logger.warning(json.dumps({"event": "approval_token_wrong_status", "status": item["status"]}))
            return False

        expires_at = datetime.fromisoformat(item["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            logger.warning(json.dumps({"event": "approval_token_expired"}))
            return False

        required = item.get("required_approvers", [])
        if required and actor_role not in required:
            logger.warning(json.dumps({"event": "approval_role_not_permitted", "role": actor_role}))
            return False

        return True
    except Exception as exc:  # noqa: BLE001
        logger.error(json.dumps({"event": "approval_validation_error", "detail": str(exc)}))
        return False
