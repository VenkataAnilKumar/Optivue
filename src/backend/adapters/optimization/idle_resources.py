"""Bedrock action group handler: detect_idle_resources."""
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import boto3

from app.config import settings

logger = logging.getLogger(__name__)
FIXTURES_DIR = Path(__file__).parents[4] / "fixtures"

_CPU_IDLE_THRESHOLD_PCT = 5.0
CW_PERIOD_SECONDS = 86400 * 14  # 14 days


def _get_ec2_cpu_utilization(instance_id: str, cw_client: Any) -> float:
    """Return average CPU utilisation for the last 14 days."""
    now = datetime.now(UTC)
    from datetime import timedelta

    start = now - timedelta(days=14)
    resp = cw_client.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=now,
        Period=CW_PERIOD_SECONDS,
        Statistics=["Average"],
    )
    datapoints = resp.get("Datapoints", [])
    if not datapoints:
        return 0.0
    return datapoints[0].get("Average", 0.0)


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Bedrock action group handler for detect_idle_resources."""
    if settings.demo_mode:
        fixture_path = FIXTURES_DIR / "sample-recommendations.json"
        data = json.loads(fixture_path.read_text()) if fixture_path.exists() else {}
        idle = [
            r for r in data.get("recommendations", [])
            if r.get("action_type") == "idle_shutdown"
        ]
        result = {
            "idle_resources": idle,
            "total": len(idle),
            "demo_mode": True,
            "data_freshness_timestamp": datetime.now(UTC).isoformat(),
        }
    else:
        ec2 = boto3.client("ec2", region_name=settings.aws_region)
        cw = boto3.client("cloudwatch", region_name=settings.aws_region)
        idle_resources = []
        try:
            resp = ec2.describe_instances(
                Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
            )
            for reservation in resp.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    iid = instance["InstanceId"]
                    cpu = _get_ec2_cpu_utilization(iid, cw)
                    if cpu < _CPU_IDLE_THRESHOLD_PCT:
                        idle_resources.append({
                            "resource_id": iid,
                            "resource_type": "EC2",
                            "instance_type": instance.get("InstanceType", ""),
                            "average_cpu_14d": round(cpu, 2),
                            "action_type": "idle_shutdown",
                            "confidence_score": 0.80,
                            "effort": "low",
                            "risk": "low",
                        })
            result = {
                "idle_resources": idle_resources,
                "total": len(idle_resources),
                "data_freshness_timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error(json.dumps({"error": "idle_detection_failed", "detail": str(exc)}))
            result = {"error": "Idle resource detection failed.", "data_freshness_timestamp": datetime.now(UTC).isoformat()}

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
