"""DynamoDB operations for recommendations, approvals, and action history."""
import logging
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

from app.config import settings

logger = logging.getLogger(__name__)


def _dynamodb_resource():
    return boto3.resource("dynamodb", region_name=settings.aws_region)


async def save_recommendation(recommendation: dict) -> str:
    """Persist a recommendation to DynamoDB."""
    db = _dynamodb_resource()
    table = db.Table(settings.dynamodb_recommendations_table)
    rec_id = recommendation["recommendation_id"]
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "pk": f"REC#{rec_id}",
        "sk": "METADATA",
        "owner": recommendation.get("suggested_owner", "unassigned"),
        "status": recommendation.get("status", "open"),
        "priority_tier": recommendation.get("priority_tier", "P3"),
        "created_at": recommendation.get("created_at", now),
        "updated_at": now,
        **recommendation,
    }
    table.put_item(Item=item)
    return rec_id


async def get_recommendations_for_owner(
    owner: str,
    priority_tier: str | None = None,
) -> list[dict]:
    """Query recommendations by owner using GSI (by-owner-status-index)."""
    db = _dynamodb_resource()
    table = db.Table(settings.dynamodb_recommendations_table)
    kwargs: dict = {
        "IndexName": "by-owner-status-index",
        "KeyConditionExpression": Key("owner").eq(owner),
    }
    response = table.query(**kwargs)
    items = response.get("Items", [])
    if priority_tier:
        items = [i for i in items if i.get("priority_tier") == priority_tier]
    return items


async def update_recommendation_status(
    recommendation_id: str,
    status: str,
    actor: str,
) -> None:
    """Update recommendation status and append to status history trail."""
    db = _dynamodb_resource()
    table = db.Table(settings.dynamodb_recommendations_table)
    now = datetime.now(timezone.utc).isoformat()
    table.update_item(
        Key={"pk": f"REC#{recommendation_id}", "sk": "METADATA"},
        UpdateExpression="SET #status = :status, updated_at = :now, last_actor = :actor",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ":status": status,
            ":now": now,
            ":actor": actor,
        },
    )
    # Append status trail entry
    table.put_item(Item={
        "pk": f"REC#{recommendation_id}",
        "sk": f"HISTORY#{now}",
        "status": status,
        "actor": actor,
        "timestamp": now,
    })


async def append_action_history(action: dict) -> None:
    """Append-only write to finops-action-history (never update or delete)."""
    db = _dynamodb_resource()
    table = db.Table(settings.dynamodb_action_history_table)
    now = datetime.now(timezone.utc).isoformat()
    table.put_item(Item={
        "pk": f"ACTION#{action['action_id']}",
        "sk": "METADATA",
        "recommendation_id": action.get("recommendation_id", ""),
        "actor": action.get("actor", ""),
        "actor_role": action.get("actor_role", ""),
        "action_type": action.get("action_type", ""),
        "result": action.get("result", "success"),
        "executed_at": now,
        **{k: v for k, v in action.items() if k not in (
            "action_id", "recommendation_id", "actor", "actor_role", "action_type", "result"
        )},
    })
