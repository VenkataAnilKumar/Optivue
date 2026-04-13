"""Shared pytest fixtures for all test layers."""
import os

import pytest

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("COGNITO_USER_POOL_ID", "us-east-1_testpool")
os.environ.setdefault("COGNITO_CLIENT_ID", "testclientid")
os.environ.setdefault("RECOMMENDATIONS_TABLE_NAME", "finops-recommendations-test")
os.environ.setdefault("APPROVALS_TABLE_NAME", "finops-approvals-test")
os.environ.setdefault("ACTION_HISTORY_TABLE_NAME", "finops-action-history-test")
os.environ.setdefault("KPI_METRICS_TABLE_NAME", "finops-kpi-metrics-test")
os.environ.setdefault("BEDROCK_AGENT_ID", "test-agent-id")
os.environ.setdefault("BEDROCK_AGENT_ALIAS_ID", "test-alias-id")
os.environ.setdefault("ATHENA_DATABASE", "finops_cost_db")
os.environ.setdefault("ATHENA_WORKGROUP", "finops-primary")
os.environ.setdefault("ATHENA_RESULTS_S3_BUCKET", "finops-athena-results-test")
os.environ.setdefault("STEP_FUNCTIONS_ARN", "arn:aws:states:us-east-1:123456789012:stateMachine:test")
os.environ.setdefault("CONFIDENCE_THRESHOLD", "0.70")


@pytest.fixture
def demo_env(monkeypatch):
    """Ensure DEMO_MODE=true for all tests."""
    monkeypatch.setenv("DEMO_MODE", "true")
    return True
