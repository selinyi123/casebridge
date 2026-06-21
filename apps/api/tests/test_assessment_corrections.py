import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def auth_headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def social_worker_headers(client: TestClient) -> dict[str, str]:
    return auth_headers(client, "demo_social_worker", "casebridge_demo_password")


def admin_headers(client: TestClient) -> dict[str, str]:
    return auth_headers(client, "demo_admin", "casebridge_admin_password")


def create_reviewed_assessment(client: TestClient) -> str:
    headers = social_worker_headers(client)
    output = client.post("/api/v1/cases/CASE-0001/ai/intake", json={"note_id": "NOTE-0001"}, headers=headers).json()["output"]
    client.patch(f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/review", json={"review_status": "accepted"}, headers=headers)
    applied = client.post(
        f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/apply-to-assessment",
        json={"reviewer_responsibility_accepted": True},
        headers=headers,
    )
    assert applied.status_code == 200
    return applied.json()["assessment"]["id"]


def test_assessment_correction_requires_admin_and_is_listed(client: TestClient) -> None:
    assessment_id = create_reviewed_assessment(client)
    social_blocked = client.post(
        f"/api/v1/cases/CASE-0001/assessments/{assessment_id}/corrections",
        json={"reason": "Needs supervisor correction.", "correction_data": {"field": "value"}},
        headers=social_worker_headers(client),
    )
    assert social_blocked.status_code == 403

    admin_created = client.post(
        f"/api/v1/cases/CASE-0001/assessments/{assessment_id}/corrections",
        json={"reason": "Supervisor correction.", "correction_data": {"missing_information": ["family check"]}},
        headers=admin_headers(client),
    )
    assert admin_created.status_code == 200
    correction = admin_created.json()["correction"]
    assert correction["event_type"] == "assessment.corrected"
    assert correction["payload"]["reviewer_role"] == "admin"

    listed = client.get(
        f"/api/v1/cases/CASE-0001/assessments/{assessment_id}/corrections",
        headers=social_worker_headers(client),
    )
    assert listed.status_code == 200
    assert correction["id"] in {item["id"] for item in listed.json()["items"]}
