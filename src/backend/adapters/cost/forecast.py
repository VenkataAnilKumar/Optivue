"""Bedrock action group handler: get_forecast."""
import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import boto3

from app.config import settings

logger = logging.getLogger(__name__)
FIXTURES_DIR = Path(__file__).parents[4] / "fixtures"

MONTHLY_ERROR_THRESHOLD = 0.15
QUARTERLY_ERROR_THRESHOLD = 0.25


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Bedrock action group handler for get_forecast."""
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    months_ahead = int(params.get("months_ahead", 1))

    if settings.demo_mode:
        fixture_path = FIXTURES_DIR / "sample-cost-data.json"
        data = json.loads(fixture_path.read_text()) if fixture_path.exists() else {}
        result = {
            "forecast": data.get("forecast", {}),
            "demo_mode": True,
            "data_freshness_timestamp": datetime.now(UTC).isoformat(),
        }
    else:
        ce = boto3.client("ce", region_name=settings.aws_region)
        start = (datetime.now(UTC) + timedelta(days=1)).strftime("%Y-%m-%d")
        end_dt = datetime.now(UTC)
        for _ in range(months_ahead):
            # advance by roughly one month
            end_dt = end_dt.replace(day=1)
            if end_dt.month == 12:
                end_dt = end_dt.replace(year=end_dt.year + 1, month=1)
            else:
                end_dt = end_dt.replace(month=end_dt.month + 1)
        end = end_dt.strftime("%Y-%m-%d")
        try:
            resp = ce.get_cost_forecast(
                TimePeriod={"Start": start, "End": end},
                Metric="UNBLENDED_COST",
                Granularity="MONTHLY",
                PredictionIntervalLevel=80,
            )
            mean = float(resp.get("Total", {}).get("Amount", 0))
            intervals = resp.get("ForecastResultsByTime", [{}])
            low = float(intervals[0].get("PredictionIntervalLowerBound", mean * 0.85))
            high = float(intervals[0].get("PredictionIntervalUpperBound", mean * 1.15))
            error_band_pct = (high - low) / mean if mean else 0
            threshold = QUARTERLY_ERROR_THRESHOLD if months_ahead >= 3 else MONTHLY_ERROR_THRESHOLD
            result = {
                "forecast_month": end,
                "mean_forecast": round(mean, 2),
                "lower_bound": round(low, 2),
                "upper_bound": round(high, 2),
                "confidence_interval_pct": 80,
                "error_band_pct": round(error_band_pct, 4),
                "forecast_reliability": "low" if error_band_pct > threshold else "high",
                "model_basis": "AWS Cost Explorer forecast API",
                "data_freshness_timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error(json.dumps({"error": "forecast_failed", "detail": str(exc)}))
            result = {"error": "Forecast failed.", "data_freshness_timestamp": datetime.now(UTC).isoformat()}

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
