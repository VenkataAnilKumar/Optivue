"""Bedrock action group handler: get_anomaly_explanation."""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import boto3

from app.config import settings

logger = logging.getLogger(__name__)
FIXTURES_DIR = Path(__file__).parents[4] / "fixtures"

_SEVERITY_THRESHOLDS = {
    "critical": 10_000,
    "high": 1_000,
    "medium": 100,
}


def _classify_severity(impact: float) -> str:
    if impact >= _SEVERITY_THRESHOLDS["critical"]:
        return "critical"
    if impact >= _SEVERITY_THRESHOLDS["high"]:
        return "high"
    if impact >= _SEVERITY_THRESHOLDS["medium"]:
        return "medium"
    return "low"


def handler(event: dict, context) -> dict:
    """Bedrock action group handler for get_anomaly_explanation."""
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    anomaly_id = params.get("anomaly_id", "")

    if settings.demo_mode:
        fixture_path = FIXTURES_DIR / "sample-anomaly.json"
        result = json.loads(fixture_path.read_text()) if fixture_path.exists() else {}
        result["demo_mode"] = True
        result["data_freshness_timestamp"] = datetime.now(timezone.utc).isoformat()
    else:
        ce = boto3.client("ce", region_name=settings.aws_region)
        try:
            resp = ce.get_anomalies(
                AnomalyMonitor={"MonitorArn": anomaly_id} if anomaly_id.startswith("arn:") else {},
                DateInterval={
                    "StartDate": "2024-01-01",
                    "EndDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                },
            )
            anomalies = resp.get("Anomalies", [])
            target = next((a for a in anomalies if a.get("AnomalyId") == anomaly_id), anomalies[0] if anomalies else {})

            impact = float(target.get("Impact", {}).get("TotalImpact", 0))
            result = {
                "anomaly_id": anomaly_id,
                "start_time": target.get("AnomalyStartDate", ""),
                "end_time": target.get("AnomalyEndDate", ""),
                "impact_amount": round(impact, 2),
                "severity": _classify_severity(impact),
                "root_cause_summary": target.get("RootCauses", [{}])[0].get("Service", "Unknown") if target.get("RootCauses") else "Unknown",
                "likely_drivers": [
                    rc.get("Service", "") for rc in target.get("RootCauses", [])
                ],
                "likely_owner": target.get("Feedback", {}).get("FeedbackType", "unassigned"),
                "data_freshness_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error(json.dumps({"error": "anomaly_fetch_failed", "detail": str(exc)}))
            result = {"error": "Anomaly lookup failed. Please retry.", "data_freshness_timestamp": datetime.now(timezone.utc).isoformat()}

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
