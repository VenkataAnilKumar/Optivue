"""Bedrock action group handler: get_recommendations with priority scoring."""
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

import boto3

from app.config import settings

logger = logging.getLogger(__name__)
FIXTURES_DIR = Path(__file__).parents[4] / "fixtures"

# Priority scoring weights (from copilot-instructions.md)
_SAVINGS_WEIGHT = 0.35
_CONFIDENCE_WEIGHT = 0.20
_EFFORT_WEIGHT = 0.20
_RISK_WEIGHT = 0.15
_STRATEGIC_WEIGHT = 0.10

_EFFORT_NORMALIZED = {"low": 0.2, "medium": 0.5, "high": 0.9}
_RISK_NORMALIZED = {"low": 0.1, "medium": 0.5, "high": 0.9}
_STRATEGIC_ALIGNMENT_DEFAULT = 0.5


def compute_priority_score(
    estimated_monthly_savings: float,
    confidence_score: float,
    effort: str,
    risk: str,
    strategic_alignment_score: float = _STRATEGIC_ALIGNMENT_DEFAULT,
) -> tuple[float, str]:
    """Compute priority_score and tier for a recommendation.

    Returns:
        (priority_score, priority_tier) where tier is P1/P2/P3.
    """
    savings_norm = min(estimated_monthly_savings / 1000.0, 1.0)
    effort_norm = _EFFORT_NORMALIZED.get(effort.lower(), 0.5)
    risk_norm = _RISK_NORMALIZED.get(risk.lower(), 0.5)

    score = (
        savings_norm * _SAVINGS_WEIGHT
        + confidence_score * _CONFIDENCE_WEIGHT
        + (1 - effort_norm) * _EFFORT_WEIGHT
        + (1 - risk_norm) * _RISK_WEIGHT
        + strategic_alignment_score * _STRATEGIC_WEIGHT
    )
    score = max(0.0, min(1.0, score))

    if score >= 0.70:
        tier = "P1"
    elif score >= 0.40:
        tier = "P2"
    else:
        tier = "P3"

    return round(score, 4), tier


def _build_recommendation(raw: dict) -> dict:
    """Augment a raw Compute Optimizer recommendation with priority fields."""
    savings = float(raw.get("estimatedMonthlySavings", 0))
    confidence = float(raw.get("confidence_score", 0.75))
    effort = raw.get("effort", "medium")
    risk = raw.get("risk", "medium")

    score, tier = compute_priority_score(savings, confidence, effort, risk)
    needs_review = confidence < settings.confidence_threshold

    return {
        **raw,
        "id": raw.get("id", str(uuid.uuid4())),
        "estimated_monthly_savings": round(savings, 2),
        "confidence_score": round(confidence, 4),
        "priority_score": score,
        "priority_tier": tier,
        "needs_review": needs_review,
        "data_freshness_timestamp": datetime.now(timezone.utc).isoformat(),
    }


def handler(event: dict, context) -> dict:
    """Bedrock action group handler for get_recommendations."""
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    service_filter = params.get("service", "")

    if settings.demo_mode:
        fixture_path = FIXTURES_DIR / "sample-recommendations.json"
        data = json.loads(fixture_path.read_text()) if fixture_path.exists() else {"recommendations": []}
        recs = [_build_recommendation(r) for r in data.get("recommendations", [])]
        result = {
            "recommendations": recs,
            "total": len(recs),
            "demo_mode": True,
            "data_freshness_timestamp": datetime.now(timezone.utc).isoformat(),
        }
    else:
        co = boto3.client("compute-optimizer", region_name=settings.aws_region)
        try:
            resp = co.get_ec2_instance_recommendations(Filters=[])
            raw_items = resp.get("instanceRecommendations", [])
            recs = []
            for item in raw_items:
                savings_obj = item.get("recommendationOptions", [{}])[0].get(
                    "estimatedMonthlySavings", {}
                )
                raw = {
                    "id": item.get("instanceArn", str(uuid.uuid4())).split(":")[-1],
                    "resource_type": "EC2",
                    "resource_id": item.get("instanceArn", ""),
                    "current_type": item.get("currentInstanceType", ""),
                    "recommended_type": item.get("recommendationOptions", [{}])[0].get(
                        "instanceType", ""
                    ),
                    "estimatedMonthlySavings": float(savings_obj.get("value", 0)),
                    "confidence_score": 0.75,
                    "effort": "medium",
                    "risk": item.get("recommendationOptions", [{}])[0].get(
                        "performanceRisk", "medium"
                    ),
                    "action_type": "rightsizing",
                    "finding": item.get("finding", ""),
                }
                if service_filter and service_filter.upper() not in raw["resource_type"].upper():
                    continue
                recs.append(_build_recommendation(raw))

            recs.sort(key=lambda r: r["priority_score"], reverse=True)
            result = {
                "recommendations": recs,
                "total": len(recs),
                "data_freshness_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error(json.dumps({"error": "recommendations_failed", "detail": str(exc)}))
            result = {"error": "Recommendations fetch failed.", "data_freshness_timestamp": datetime.now(timezone.utc).isoformat()}

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
