from adapters.governance.approval import _required_approvers


def test_required_approvers_prod_rightsizing_dual() -> None:
	approvers = _required_approvers("prod", "rightsizing")
	assert "engineering-manager" in approvers
	assert "finops-analyst" in approvers
	assert len(approvers) == 2


def test_required_approvers_staging_default_single() -> None:
	approvers = _required_approvers("staging", "unknown-action")
	assert approvers == ["finops-analyst"]


def test_required_approvers_dev_default_auto_approved() -> None:
	approvers = _required_approvers("dev", "rightsizing")
	assert approvers == []

