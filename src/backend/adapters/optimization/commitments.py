"""Bedrock action group handler: analyze_commitment_opportunities."""
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import boto3

from app.config import settings

logger = logging.getLogger(__name__)
FIXTURES_DIR = Path(__file__).parents[4] / "fixtures"


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Bedrock action group handler for analyze_commitment_opportunities."""
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    term_years = int(params.get("term_years", 1))
    payment_option = params.get("payment_option", "NO_UPFRONT")

    if settings.demo_mode:
        fixture_path = FIXTURES_DIR / "sample-recommendations.json"
        data = json.loads(fixture_path.read_text()) if fixture_path.exists() else {}
        commitments = [
            r for r in data.get("recommendations", [])
            if r.get("action_type") == "commitment_purchase"
        ]
        result = {
            "commitments": commitments,
            "total": len(commitments),
            "demo_mode": True,
            "data_freshness_timestamp": datetime.now(UTC).isoformat(),
        }
    else:
        ce = boto3.client("ce", region_name=settings.aws_region)
        try:
            resp = ce.get_savings_plans_purchase_recommendation(
                SavingsPlansType="COMPUTE_SP",
                TermInYears="ONE_YEAR" if term_years == 1 else "THREE_YEARS",
                PaymentOption=payment_option,
                LookbackPeriodInDays="SIXTY_DAYS",
            )
            recommendation = resp.get("SavingsPlansPurchaseRecommendation", {})
            _details = recommendation.get("SavingsPlansDetails", [])  # reserved for per-plan breakdown
            summary = recommendation.get("SavingsPlansPurchaseRecommendationSummary", {})

            result = {
                "commitment_type": "Compute Savings Plan",
                "term_years": term_years,
                "payment_option": payment_option,
                "estimated_monthly_savings": round(
                    float(summary.get("EstimatedMonthlySavingsAmount", 0)), 2
                ),
                "estimated_savings_percentage": round(
                    float(summary.get("EstimatedSavingsPercentage", 0)), 2
                ),
                "recommended_hourly_commitment": round(
                    float(summary.get("HourlyCommitmentToPurchase", 0)), 4
                ),
                "upfront_cost": round(float(summary.get("TotalPaymentDue", 0)), 2),
                "action_type": "commitment_purchase",
                "confidence_score": 0.85,
                "effort": "low",
                "risk": "medium",
                "data_freshness_timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error(json.dumps({"error": "commitments_failed", "detail": str(exc)}))
            result = {"error": "Commitment analysis failed.", "data_freshness_timestamp": datetime.now(UTC).isoformat()}

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
