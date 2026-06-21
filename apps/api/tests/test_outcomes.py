import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_create_service_outcome_records_manual_gas_score(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cases/CASE-0001/outcomes",
        json={"gas_score": 1, "narrative": "Manual follow-up shows partial progress.", "evidence": "Demo evidence."},
    )
    assert response.status_code == 200
    outcome = response.json()["outcome"]
    assert outcome["case_id"] == "CASE-0001"
    assert outcome["gas_score"] == 1
    assert outcome["recorded_by"] == "demo_social_worker"

    listed = client.get("/api/v1/cases/CASE-0001/outcomes").json()["items"]
    assert outcome["id"] in {item["id"] for item in listed}


def test_service_outcome_rejects_invalid_gas_score(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cases/CASE-0001/outcomes",
        json={"gas_score": 3, "narrative": "Invalid score."},
    )
    assert response.status_code == 422
