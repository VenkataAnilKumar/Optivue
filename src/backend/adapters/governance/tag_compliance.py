"""Bedrock action group handler: check_tag_compliance."""
import json
import logging
from datetime import UTC, datetime
from typing import Any

import boto3

from app.config import settings

logger = logging.getLogger(__name__)

_REQUIRED_TAGS = ["environment", "team", "product", "cost-center"]


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Bedrock action group handler for check_tag_compliance."""
    params = {p["name"]: p["value"] for p in event.get("parameters", [])}
    resource_type_filter = params.get("resource_type", "")

    if settings.demo_mode:
        result = {
            "total_resources": 150,
            "compliant": 110,
            "non_compliant": 40,
            "compliance_percentage": 73.3,
            "required_tags": _REQUIRED_TAGS,
            "top_violators": [
                {"resource_id": "i-demo1234", "missing_tags": ["cost-center", "product"]},
                {"resource_id": "i-demo5678", "missing_tags": ["team"]},
            ],
            "demo_mode": True,
            "data_freshness_timestamp": datetime.now(UTC).isoformat(),
        }
    else:
        config = boto3.client("config", region_name=settings.aws_region)
        try:
            resp = config.list_discovered_resources(
                resourceType=resource_type_filter or "AWS::EC2::Instance",
                limit=100,
            )
            resources = resp.get("resourceIdentifiers", [])
            total = len(resources)
            non_compliant = []

            for res in resources:
                rid = res["resourceId"]
                _rtype = res["resourceType"]  # reserved for type-scoped compliance rules
                tag_resp = config.list_tags_for_resource(
                    ResourceArn=res.get("resourceName", rid)
                )
                existing_keys = {t["key"].lower() for t in tag_resp.get("Tags", [])}
                missing = [t for t in _REQUIRED_TAGS if t not in existing_keys]
                if missing:
                    non_compliant.append({"resource_id": rid, "missing_tags": missing})

            compliant_count = total - len(non_compliant)
            compliance_pct = (compliant_count / total * 100) if total else 100.0

            result = {
                "total_resources": total,
                "compliant": compliant_count,
                "non_compliant": len(non_compliant),
                "compliance_percentage": round(compliance_pct, 1),
                "required_tags": _REQUIRED_TAGS,
                "top_violators": non_compliant[:10],
                "data_freshness_timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error(json.dumps({"error": "tag_compliance_failed", "detail": str(exc)}))
            result = {"error": "Tag compliance check failed.", "data_freshness_timestamp": datetime.now(UTC).isoformat()}

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
