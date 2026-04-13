"""Seed finops-recommendations DynamoDB table from fixture data.

Usage:
	python scripts/seed/seed-dynamo.py

Required env vars:
	RECOMMENDATIONS_TABLE_NAME   (default: finops-recommendations)
	AWS_REGION_NAME              (default: us-east-1)
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import boto3


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "fixtures" / "sample-recommendations.json"


def _normalize_record(raw: dict[str, Any]) -> dict[str, Any]:
	now = datetime.now(timezone.utc).isoformat()
	rec_id = raw.get("recommendation_id") or raw.get("id") or f"rec-{int(datetime.now(timezone.utc).timestamp())}"
	priority_tier = raw.get("priority_tier", "P2")
	status = raw.get("status", "new")

	return {
		"pk": f"REC#{rec_id}",
		"sk": "METADATA",
		"id": rec_id,
		"resource_type": raw.get("resource_type", "unknown"),
		"resource_id": raw.get("resource_id", raw.get("resource_ids", ["unknown"])[0]),
		"account_id": raw.get("account_id", "000000000000"),
		"region": raw.get("region", "us-east-1"),
		"action_type": raw.get("type", raw.get("action_type", "other")),
		"title": raw.get("title", f"Optimization recommendation {rec_id}"),
		"description": raw.get("rationale", raw.get("description", "No description provided.")),
		"estimated_monthly_savings": float(raw.get("estimated_monthly_savings", 0.0)),
		"confidence_score": float(raw.get("confidence_score", 0.7)),
		"effort": raw.get("effort", raw.get("effort_level", "medium")),
		"risk": raw.get("risk", raw.get("risk_level", "medium")),
		"priority_score": float(raw.get("priority_score", 0.5)),
		"priority_tier": priority_tier,
		"needs_review": bool(raw.get("needs_review", False)),
		"status": status,
		"owner": raw.get("suggested_owner", raw.get("owner", "unassigned")),
		"created_at": now,
		"updated_at": now,
		"data_freshness_timestamp": now,
		"evidence_refs": raw.get("evidence_refs", []),
	}


def main() -> None:
	table_name = os.getenv("RECOMMENDATIONS_TABLE_NAME", "finops-recommendations")
	region = os.getenv("AWS_REGION_NAME", "us-east-1")

	if not FIXTURE_PATH.exists():
		raise FileNotFoundError(f"Fixture not found: {FIXTURE_PATH}")

	payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
	recommendations = payload.get("recommendations", [])

	ddb = boto3.resource("dynamodb", region_name=region)
	table = ddb.Table(table_name)

	inserted = 0
	for raw in recommendations:
		item = _normalize_record(raw)
		table.put_item(Item=item)
		inserted += 1

	print(json.dumps({"table": table_name, "inserted": inserted}, indent=2))


if __name__ == "__main__":
	main()

