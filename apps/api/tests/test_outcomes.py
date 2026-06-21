import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "demo_social_worker", "password": "casebridge_demo_password"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_service_outcome_records_manual_gas_score(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cases/CASE-0001/outcomes",
        json={"gas_score": 1, "narrative": "Manual follow-up shows partial progress.", "evidence": "Demo evidence."},
        headers=auth_headers(client),
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
        headers=auth_headers(client),
    )
    assert response.status_code == 422


def test_outcome_appears_in_timeline(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cases/CASE-0001/outcomes",
        json={"gas_score": 0, "narrative": "Timeline outcome check."},
        headers=auth_headers(client),
    )
    assert response.status_code == 200
    outcome_id = response.json()["outcome"]["id"]

    timeline = client.get("/api/v1/cases/CASE-0001/timeline").json()["items"]
    outcome_items = [item for item in timeline if item["kind"] == "outcome"]
    assert outcome_id in {item["id"] for item in outcome_items}


def test_schema_catalog_alias_is_available(client: TestClient) -> None:
    response = client.get("/api/v1/cases/CASE-0001/outcomes/schema/community-intake-v0.1.10")
    assert response.status_code == 200
    schema = response.json()["schema"]
    assert schema["schema_id"] == "community-intake-v0.1.10"
    assert "meal_nutrition" in schema["domains"]
