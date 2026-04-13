"""Bedrock action group handler: get_cost_by_period."""
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import boto3

from app.config import settings

logger = logging.getLogger(__name__)
FIXTURES_DIR = Path(__file__).parents[4] / "fixtures"


def _run_athena_query(sql: str) -> list[dict]:
    """Execute an Athena query and return rows as list of dicts."""
    client = boto3.client("athena", region_name=settings.aws_region)
    response = client.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": settings.athena_database},
        WorkGroup=settings.athena_workgroup,
        ResultConfiguration={
            "OutputLocation": f"s3://{settings.athena_results_s3_bucket}/query-results/"
        },
    )
    execution_id = response["QueryExecutionId"]

    # Poll for completion (max 30s)
    for _ in range(60):
        status_resp = client.get_query_execution(QueryExecutionId=execution_id)
        state = status_resp["QueryExecution"]["Status"]["State"]
        if state == "SUCCEEDED":
            break
        if state in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"Athena query {state}: {execution_id}")
        time.sleep(0.5)

    results = client.get_query_results(QueryExecutionId=execution_id)
    cols = [c["Label"] for c in results["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]]
    rows = []
    for row in results["ResultSet"]["Rows"][1:]:  # skip header
        values = [d.get("VarCharValue", "") for d in row["Data"]]
        rows.append(dict(zip(cols, values)))
    return rows


def handler(event: dict, context) -> dict:
    """Bedrock action group handler for get_cost_by_period."""
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    period = params.get("period", "last_month")
    _granularity = params.get("granularity", "MONTHLY")  # reserved for future Athena query parameterisation

    if settings.demo_mode:
        fixture_path = FIXTURES_DIR / "sample-cost-data.json"
        result = json.loads(fixture_path.read_text()) if fixture_path.exists() else {}
        result["demo_mode"] = True
        result["data_freshness_timestamp"] = datetime.now(timezone.utc).isoformat()
    else:
        sql = f"""
            SELECT line_item_product_code AS service,
                   SUM(line_item_unblended_cost) AS cost
            FROM {settings.athena_database}.cost_and_usage
            WHERE line_item_usage_start_date >= date_trunc('month', current_date - interval '1' month)
              AND line_item_usage_start_date < date_trunc('month', current_date)
            GROUP BY line_item_product_code
            ORDER BY cost DESC
            LIMIT 10
        """
        try:
            rows = _run_athena_query(sql)
            total = sum(float(r.get("cost", 0)) for r in rows)
            result = {
                "total_cost": round(total, 2),
                "currency": "USD",
                "period": period,
                "top_drivers": [
                    {"service": r["service"], "cost": round(float(r["cost"]), 2)}
                    for r in rows
                ],
                "data_freshness_timestamp": datetime.now(timezone.utc).isoformat(),
                "data_completeness_pct": 100.0,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error(json.dumps({"error": "athena_query_failed", "detail": str(exc)}))
            result = {"error": "Cost query failed. Please retry.", "data_freshness_timestamp": datetime.now(timezone.utc).isoformat()}

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
