"""Slack/Teams notification adapter for action ownership."""
import json
import logging
from datetime import UTC, datetime
from typing import Any

import boto3
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _get_webhook_url() -> str:
    """Fetch Slack webhook URL from Secrets Manager."""
    if settings.demo_mode:
        return "https://hooks.slack.com/demo"
    sm = boto3.client("secretsmanager", region_name=settings.aws_region)
    secret = json.loads(
        sm.get_secret_value(SecretId="finops/slack-webhook-url")["SecretString"]
    )
    return secret["webhook_url"]


def _build_slack_blocks(
    recommendation_id: str,
    ticket_url: str | None,
    actor: str,
) -> list[dict[str, Any]]:
    """Build Slack Block Kit message for owner notification."""
    blocks: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": ":money_with_wings: FinOps Action Approved"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Recommendation:*\n{recommendation_id[:16]}..."},
                {"type": "mrkdwn", "text": f"*Approved by:*\n{actor}"},
            ],
        },
    ]
    if ticket_url:
        blocks.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Jira Ticket"},
                        "url": ticket_url,
                        "style": "primary",
                    }
                ],
            }
        )
    return blocks


async def send_owner_notification(
    recommendation_id: str,
    ticket_url: str | None,
    actor: str,
    channel: str = "#finops-actions",
) -> dict[str, Any]:
    """Send Slack notification to resource owner.

    Called only AFTER ticket creation succeeds.
    """
    webhook_url = _get_webhook_url()
    blocks = _build_slack_blocks(recommendation_id, ticket_url, actor)

    if settings.demo_mode:
        logger.info(json.dumps({
            "event": "demo_notification_sent",
            "recommendation_id": recommendation_id,
            "channel": channel,
        }))
        result = {"notification_sent": True, "channel": channel, "demo_mode": True}
    else:
        payload = {
            "channel": channel,
            "blocks": blocks,
            "text": f"FinOps action approved for recommendation {recommendation_id[:16]}",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                resp.raise_for_status()
            result = {"notification_sent": True, "channel": channel}
        except httpx.HTTPError as exc:
            # Graceful degradation — notification failure must not crash the primary path
            logger.error(json.dumps({"event": "slack_notification_failed", "detail": str(exc)}))
            result = {"notification_sent": False, "channel": channel, "error": "Notification failed gracefully"}

    # Append to action-history (PutItem only)
    dynamo = boto3.resource("dynamodb", region_name=settings.aws_region)
    table = dynamo.Table(settings.action_history_table_name)
    table.put_item(Item={
        "pk": f"ACTION#{recommendation_id}",
        "sk": f"HISTORY#{datetime.now(UTC).isoformat()}",
        "event_type": "owner_notified",
        "recommendation_id": recommendation_id,
        "ticket_url": ticket_url or "",
        "channel": channel,
        "actor": actor,
        "notification_sent": result["notification_sent"],
        "created_at": datetime.now(UTC).isoformat(),
    })

    return result

