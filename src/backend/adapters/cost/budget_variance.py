"""Bedrock action group handler: get_budget_variance."""
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import boto3

from app.config import settings

logger = logging.getLogger(__name__)
FIXTURES_DIR = Path(__file__).parents[4] / "fixtures"


def _variance_status(variance_pct: float) -> str:
    if variance_pct <= -10:
        return "under_budget"
    if variance_pct <= 5:
        return "on_track"
    if variance_pct <= 15:
        return "at_risk"
    return "over_budget"


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Bedrock action group handler for get_budget_variance."""
    if settings.demo_mode:
        fixture_path = FIXTURES_DIR / "sample-cost-data.json"
        data = json.loads(fixture_path.read_text()) if fixture_path.exists() else {}
        result = {
            "budgets": data.get("budgets", []),
            "demo_mode": True,
            "data_freshness_timestamp": datetime.now(UTC).isoformat(),
        }
    else:
        budgets_client = boto3.client("budgets", region_name=settings.aws_region)
        sts = boto3.client("sts", region_name=settings.aws_region)
        account_id = sts.get_caller_identity()["Account"]
        try:
            resp = budgets_client.describe_budgets(AccountId=account_id)
            budgets = []
            for budget in resp.get("Budgets", []):
                budget_amount = float(budget.get("BudgetLimit", {}).get("Amount", 0))
                actual_spend = float(
                    budget.get("CalculatedSpend", {}).get("ActualSpend", {}).get("Amount", 0)
                )
                variance = actual_spend - budget_amount
                variance_pct = (variance / budget_amount * 100) if budget_amount else 0
                budgets.append({
                    "budget_name": budget.get("BudgetName", ""),
                    "budgeted_amount": round(budget_amount, 2),
                    "actual_amount": round(actual_spend, 2),
                    "variance_amount": round(variance, 2),
                    "variance_pct": round(variance_pct, 2),
                    "status": _variance_status(variance_pct),
                })
            result = {
                "budgets": budgets,
                "data_freshness_timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error(json.dumps({"error": "budget_variance_failed", "detail": str(exc)}))
            result = {"error": "Budget variance query failed.", "data_freshness_timestamp": datetime.now(UTC).isoformat()}

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
