from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_execute_action_rejects_invalid_token() -> None:
	client = TestClient(app)

	with patch("app.routers.actions.validate_approval_token", new=AsyncMock(return_value=False)):
		response = client.post(
			"/actions/execute",
			json={
				"approval_request_id": "app-1",
				"recommendation_id": "rec-1",
				"action_type": "create_ticket",
				"approval_token": "bad-token",
			},
		)
	assert response.status_code == 403


def test_execute_action_create_ticket_success_path() -> None:
	client = TestClient(app)

	with patch("app.routers.actions.validate_approval_token", new=AsyncMock(return_value=True)), patch(
		"app.routers.actions.create_jira_ticket",
		new=AsyncMock(return_value={"ticket_id": "FINOPS-123", "ticket_url": "https://jira/FINOPS-123", "status": "created"}),
	):
		response = client.post(
			"/actions/execute",
			json={
				"approval_request_id": "app-1",
				"recommendation_id": "rec-1",
				"action_type": "create_ticket",
				"approval_token": "ok-token",
			},
		)
	assert response.status_code == 200
	assert response.json()["ticket_id"] == "FINOPS-123"

