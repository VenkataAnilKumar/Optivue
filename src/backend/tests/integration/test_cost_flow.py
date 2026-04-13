from fastapi.testclient import TestClient

from app.main import app


def test_cost_query_endpoint_returns_data_shape() -> None:
	client = TestClient(app)
	response = client.get("/cost/query?period=last_month")
	assert response.status_code == 200
	data = response.json()
	assert data.get("demo_mode") is True
	assert "query" in data
	assert "result" in data


def test_forecast_endpoint_returns_reliability() -> None:
	client = TestClient(app)
	response = client.get("/cost/forecast?months_ahead=1")
	assert response.status_code == 200
	data = response.json()
	assert data.get("demo_mode") is True
	assert "result" in data

