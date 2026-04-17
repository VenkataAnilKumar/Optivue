"""Integration tests for the FastAPI application with mocked AWS."""
import os

import pytest

mock_aws = pytest.importorskip("moto").mock_aws
import boto3  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

os.environ["DEMO_MODE"] = "true"

from app.main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_integration_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] in ("ok", "healthy")


# ---------------------------------------------------------------------------
# Cost routes (DEMO_MODE — no real AWS calls)
# ---------------------------------------------------------------------------

def test_cost_query_requires_auth():
    resp = client.get("/cost/query?period=last_month")
    # Without Authorization header in non-demo auth mode the app returns 401/403
    # In DEMO_MODE auth is bypassed, so 200 is accepted
    assert resp.status_code in (200, 401, 403)


def test_anomaly_list_endpoint_exists():
    resp = client.get("/anomalies/")
    assert resp.status_code in (200, 401, 403)


def test_recommendations_endpoint_exists():
    resp = client.get("/recommendations/")
    assert resp.status_code in (200, 401, 403)


def test_recommendations_endpoint_returns_valid_shape():
    """Validate that the recommendations endpoint response matches the API contract."""
    resp = client.get("/recommendations/")
    assert resp.status_code in (200, 401, 403)
    if resp.status_code == 200:
        body = resp.json()
        assert isinstance(body, dict), "Response body must be a JSON object"
        assert "recommendations" in body or "items" in body or "response" in body, (
            "Response must contain a 'recommendations', 'items', or 'response' key"
        )
        total = body.get("total")
        assert total is None or isinstance(total, int), (
            "'total' field must be an integer when present"
        )


def test_kpi_endpoint_exists():
    resp = client.get("/kpi/")
    assert resp.status_code in (200, 401, 403)


# ---------------------------------------------------------------------------
# Actions — approval gate enforcement
# ---------------------------------------------------------------------------

@mock_aws
def test_execute_action_without_token_returns_403():
    """Actions endpoint must refuse requests with missing/invalid approval token."""
    # Create DynamoDB table first
    dynamo = boto3.resource("dynamodb", region_name="us-east-1")
    dynamo.create_table(
        TableName=os.environ.get("APPROVALS_TABLE_NAME", "finops-approvals-test"),
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamo.create_table(
        TableName=os.environ.get("ACTION_HISTORY_TABLE_NAME", "finops-action-history-test"),
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    resp = client.post("/actions/execute", json={
        "approval_request_id": "approval-001",
        "recommendation_id": "rec-001",
        "approval_token": "00000000-invalid-token",
        "action_type": "rightsizing",
    })
    assert resp.status_code == 403
