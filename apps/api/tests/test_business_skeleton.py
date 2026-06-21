import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_client_profile_exists(client: TestClient) -> None:
    response = client.get("/api/v1/clients/C-0001")
    assert response.status_code == 200
    payload = response.json()
    assert payload["client"]["code"] == "C-0001"
    assert payload["cases"][0]["id"] == "CASE-0001"


def test_resource_matching_is_deterministic(client: TestClient) -> None:
    response = client.post(
        "/api/v1/resources/match",
        json={"need_tag_codes": ["meal_difficulty", "mobility_limited", "living_alone"]},
    )
    assert response.status_code == 200
    candidates = response.json()["candidates"]
    codes = {item["resource_code"] for item in candidates}
    assert "R-001" in codes
    assert "R-003" in codes
    assert "R-005" in codes


def test_resource_match_rejects_invalid_body_type(client: TestClient) -> None:
    response = client.post("/api/v1/resources/match", json={"need_tag_codes": "meal_difficulty"})
    assert response.status_code == 422


def test_create_case_note_preserves_raw_content(client: TestClient) -> None:
    raw = "Synthetic visit note for C-0001."
    response = client.post(
        "/api/v1/cases/CASE-0001/notes",
        json={"note_type": "visit", "content_raw": raw},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["note"]["content_raw"] == raw
    assert payload["note"]["content_clean"] == raw
    assert payload["note"]["source"] == "human"


def test_created_note_is_visible_in_case_timeline(client: TestClient) -> None:
    raw = "Timeline visibility note for C-0001."
    create_response = client.post(
        "/api/v1/cases/CASE-0001/notes",
        json={"note_type": "visit", "content_raw": raw},
    )
    assert create_response.status_code == 200
    note_id = create_response.json()["note"]["id"]

    timeline_response = client.get("/api/v1/cases/CASE-0001/notes")
    assert timeline_response.status_code == 200
    note_ids = {item["id"] for item in timeline_response.json()["items"]}
    assert note_id in note_ids


def test_create_case_note_rejects_blank_content(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cases/CASE-0001/notes",
        json={"note_type": "visit", "content_raw": ""},
    )
    assert response.status_code == 422


def test_redactor_masks_long_digit_run(client: TestClient) -> None:
    raw = "demo 13800000000"
    response = client.post(
        "/api/v1/cases/CASE-0001/notes",
        json={"note_type": "visit", "content_raw": raw},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "[REDACTED_PHONE]" in payload["note"]["content_clean"]
    assert payload["note"]["pii_detected"] is True


def test_create_service_goal(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cases/CASE-0001/goals",
        json={"title": "建立稳定餐食支持", "target_state": "完成助餐资源核实并形成跟进安排"},
    )
    assert response.status_code == 200
    goal = response.json()["goal"]
    assert goal["case_id"] == "CASE-0001"
    assert goal["status"] == "not_started"

    list_response = client.get("/api/v1/cases/CASE-0001/goals")
    assert list_response.status_code == 200
    goal_ids = {item["id"] for item in list_response.json()["items"]}
    assert goal["id"] in goal_ids


def test_create_resource_link_candidate(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cases/CASE-0001/referrals",
        json={"resource_code": "R-001", "agreement_status": "none", "notes": "candidate only"},
    )
    assert response.status_code == 200
    referral = response.json()["referral"]
    assert referral["resource_code"] == "R-001"
    assert referral["status"] == "to_verify"
    assert referral["agreement_status"] == "none"


def test_resource_link_requires_agreement_before_referred(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/cases/CASE-0001/referrals",
        json={"resource_code": "R-003", "agreement_status": "none"},
    )
    assert create_response.status_code == 200
    referral_id = create_response.json()["referral"]["id"]

    blocked_response = client.patch(
        f"/api/v1/cases/CASE-0001/referrals/{referral_id}/status",
        json={"status": "referred"},
    )
    assert blocked_response.status_code == 409

    allowed_response = client.patch(
        f"/api/v1/cases/CASE-0001/referrals/{referral_id}/status",
        json={"status": "referred", "agreement_status": "verbal"},
    )
    assert allowed_response.status_code == 200
    assert allowed_response.json()["referral"]["status"] == "referred"


def test_unified_timeline_contains_manual_events(client: TestClient) -> None:
    goal_response = client.post(
        "/api/v1/cases/CASE-0001/goals",
        json={"title": "timeline goal", "target_state": "visible in unified timeline"},
    )
    assert goal_response.status_code == 200
    link_response = client.post(
        "/api/v1/cases/CASE-0001/referrals",
        json={"resource_code": "R-005", "agreement_status": "none"},
    )
    assert link_response.status_code == 200

    timeline_response = client.get("/api/v1/cases/CASE-0001/timeline")
    assert timeline_response.status_code == 200
    kinds = {item["kind"] for item in timeline_response.json()["items"]}
    assert "note" in kinds
    assert "goal" in kinds
    assert "resource_link" in kinds
    assert "audit" in kinds
