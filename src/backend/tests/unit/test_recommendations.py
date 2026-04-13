from adapters.optimization.recommendations import (
	_build_recommendation,
	compute_priority_score,
)


def test_priority_scoring_p1_for_high_value_low_risk() -> None:
	score, tier = compute_priority_score(estimated_monthly_savings=1200, confidence_score=0.9, effort="low", risk="low")
	assert score >= 0.70
	assert tier == "P1"


def test_priority_scoring_p3_for_low_value_high_risk() -> None:
	score, tier = compute_priority_score(estimated_monthly_savings=50, confidence_score=0.4, effort="high", risk="high")
	assert score < 0.40
	assert tier == "P3"


def test_build_recommendation_marks_needs_review_below_threshold() -> None:
	rec = _build_recommendation(
		{
			"id": "rec-low-confidence",
			"estimatedMonthlySavings": 500,
			"confidence_score": 0.3,
			"effort": "medium",
			"risk": "medium",
		}
	)
	assert rec["needs_review"] is True
	assert rec["priority_tier"] in {"P1", "P2", "P3"}

