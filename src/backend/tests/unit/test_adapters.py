"""Unit tests for Bedrock action group adapter response shapes."""
import json
import os


os.environ["DEMO_MODE"] = "true"


def _check_bedrock_response_shape(result: dict) -> None:
    """Assert the Bedrock action group response contract."""
    assert result["messageVersion"] == "1.0"
    resp = result["response"]
    assert "actionGroup" in resp
    assert "function" in resp
    body = resp["functionResponse"]["responseBody"]["TEXT"]["body"]
    parsed = json.loads(body)
    assert isinstance(parsed, dict)
    return parsed


def _fake_event(action_group: str, function: str, params: list[dict] | None = None) -> dict:
    return {
        "actionGroup": action_group,
        "function": function,
        "parameters": params or [],
    }


def test_cost_query_response_shape():
    from adapters.cost.cost_query import handler
    event = _fake_event("cost-analysis", "get_cost_by_period")
    result = handler(event, None)
    parsed = _check_bedrock_response_shape(result)
    assert "data_freshness_timestamp" in parsed


def test_anomaly_explain_response_shape():
    from adapters.cost.anomaly_explain import handler
    event = _fake_event("cost-analysis", "get_anomaly_explanation",
                        [{"name": "anomaly_id", "value": "anomaly-demo-001"}])
    result = handler(event, None)
    parsed = _check_bedrock_response_shape(result)
    assert "data_freshness_timestamp" in parsed


def test_budget_variance_response_shape():
    from adapters.cost.budget_variance import handler
    event = _fake_event("cost-analysis", "get_budget_variance")
    result = handler(event, None)
    parsed = _check_bedrock_response_shape(result)
    assert "data_freshness_timestamp" in parsed


def test_forecast_response_shape():
    from adapters.cost.forecast import handler
    event = _fake_event("cost-analysis", "get_forecast",
                        [{"name": "months_ahead", "value": "1"}])
    result = handler(event, None)
    parsed = _check_bedrock_response_shape(result)
    assert "data_freshness_timestamp" in parsed


def test_recommendations_response_shape():
    from adapters.optimization.recommendations import handler
    event = _fake_event("optimization", "get_recommendations")
    result = handler(event, None)
    parsed = _check_bedrock_response_shape(result)
    assert "recommendations" in parsed
    assert "data_freshness_timestamp" in parsed


def test_recommendation_has_priority_fields():
    from adapters.optimization.recommendations import handler
    event = _fake_event("optimization", "get_recommendations")
    result = handler(event, None)
    parsed = json.loads(result["response"]["functionResponse"]["responseBody"]["TEXT"]["body"])
    recs = parsed.get("recommendations", [])
    if recs:
        rec = recs[0]
        assert "priority_score" in rec
        assert "priority_tier" in rec
        assert "needs_review" in rec
        assert "confidence_score" in rec


def test_risk_eval_blocks_production_deletion():
    from adapters.governance.risk_eval import evaluate_risk
    result = evaluate_risk("delete", "prod-database-01", "prod")
    assert result["policy_blocked"] is True
    assert result["block_reason"] is not None


def test_risk_eval_allows_rightsizing():
    from adapters.governance.risk_eval import evaluate_risk
    result = evaluate_risk("rightsizing", "i-0abc1234", "prod")
    assert result["policy_blocked"] is False
