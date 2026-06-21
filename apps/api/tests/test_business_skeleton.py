from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_client_profile_exists() -> None:
    response = client.get("/api/v1/clients/C-0001")
    assert response.status_code == 200
    payload = response.json()
    assert payload["client"]["code"] == "C-0001"
    assert payload["cases"][0]["id"] == "CASE-0001"


def test_resource_matching_is_deterministic() -> None:
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


def test_resource_match_rejects_invalid_body_type() -> None:
    response = client.post("/api/v1/resources/match", json={"need_tag_codes": "meal_difficulty"})
    assert response.status_code == 422


def test_create_case_note_preserves_raw_content() -> None:
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


def test_create_case_note_rejects_blank_content() -> None:
    response = client.post(
        "/api/v1/cases/CASE-0001/notes",
        json={"note_type": "visit", "content_raw": ""},
    )
    assert response.status_code == 422


def test_redactor_masks_long_digit_run() -> None:
    raw = "demo 13800000000"
    response = client.post(
        "/api/v1/cases/CASE-0001/notes",
        json={"note_type": "visit", "content_raw": raw},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "[REDACTED_PHONE]" in payload["note"]["content_clean"]
    assert payload["note"]["pii_detected"] is True
