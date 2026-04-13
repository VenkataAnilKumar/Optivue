"""KPI computation and snapshot service."""
import json
import logging
from datetime import UTC, datetime
from typing import Any, cast

import boto3
from boto3.dynamodb.conditions import Key

from app.config import settings

logger = logging.getLogger(__name__)


def _dynamodb_resource() -> Any:
    return boto3.resource("dynamodb", region_name=settings.aws_region)


async def compute_weekly_kpis() -> dict[str, Any]:
    """Compute weekly KPI snapshot and write to finops-kpi-metrics."""
    db = _dynamodb_resource()
    recs_table = db.Table(settings.dynamodb_recommendations_table)
    history_table = db.Table(settings.dynamodb_action_history_table)
    kpi_table = db.Table(settings.dynamodb_kpi_table)

    # Scan recommendations for acceptance/completion rates
    recs_response = recs_table.scan(
        FilterExpression="begins_with(sk, :meta)",
        ExpressionAttributeValues={":meta": "METADATA"},
    )
    all_recs = cast(list[dict[str, Any]], recs_response.get("Items", []))
    open_recs = [r for r in all_recs if r.get("status") == "open"]
    acknowledged = [r for r in all_recs if r.get("status") in ("acknowledged", "in_progress", "completed")]
    completed = [r for r in all_recs if r.get("status") == "completed"]
    total = len(all_recs)

    acceptance_rate = len(acknowledged) / total if total > 0 else 0.0
    completion_rate = len(completed) / total if total > 0 else 0.0

    # Safety violations: scan action history for result=blocked
    history_response = history_table.scan(
        FilterExpression="#result = :blocked",
        ExpressionAttributeNames={"#result": "result"},
        ExpressionAttributeValues={":blocked": "blocked"},
    )
    safety_violations = len(cast(list[dict[str, Any]], history_response.get("Items", [])))

    now = datetime.now(UTC).isoformat()
    week_key = datetime.now(UTC).strftime("%Y-W%W")

    kpi_snapshot = {
        "recommendation_acceptance_rate": round(acceptance_rate, 4),
        "recommendation_completion_rate": round(completion_rate, 4),
        "action_safety_violations": safety_violations,
        "total_recommendations": total,
        "open_recommendations": len(open_recs),
        "completed_recommendations": len(completed),
        "computed_at": now,
    }

    kpi_table.put_item(Item={
        "pk": "KPI#weekly",
        "sk": week_key,
        **kpi_snapshot,
    })

    # Emit CloudWatch metric for safety violations
    if safety_violations > 0:
        cw = boto3.client("cloudwatch", region_name=settings.aws_region)
        cw.put_metric_data(
            Namespace="finops",
            MetricData=[{
                "MetricName": "ActionSafetyViolations",
                "Value": float(safety_violations),
                "Unit": "Count",
            }],
        )
        logger.error(json.dumps({
            "event": "safety_violation_detected",
            "count": safety_violations,
            "week": week_key,
        }))

    return kpi_snapshot


async def get_latest_kpis() -> dict[str, Any]:
    """Retrieve the most recent weekly KPI snapshot."""
    try:
        db = _dynamodb_resource()
        kpi_table = db.Table(settings.dynamodb_kpi_table)
        response = kpi_table.query(
            KeyConditionExpression=Key("pk").eq("KPI#weekly"),
            ScanIndexForward=False,
            Limit=1,
        )
        items = cast(list[dict[str, Any]], response.get("Items", []))
        if not items:
            return {"message": "No KPI data available yet.", "demo_mode": settings.demo_mode}
        return items[0]
    except Exception as exc:  # noqa: BLE001
        logger.warning(json.dumps({"event": "kpi_read_fallback", "detail": str(exc)}))
        return {"message": "KPI service unavailable.", "demo_mode": settings.demo_mode}

