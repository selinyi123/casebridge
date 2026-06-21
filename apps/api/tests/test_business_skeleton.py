import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.ai.mock_provider import generate_intake_draft
from app.ai.prompt_registry import get_prompt_spec
from app.ai.provider_registry import generate_with_provider
from app.ai.redaction_gateway import run_redaction_gate
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
    response = client.post("/api/v1/resources/match", json={"need_tag_codes": ["meal_difficulty", "mobility_limited", "living_alone"]})
    assert response.status_code == 200
    codes = {item["resource_code"] for item in response.json()["candidates"]}
    assert "R-001" in codes
    assert "R-003" in codes
    assert "R-005" in codes


def test_resource_match_rejects_invalid_body_type(client: TestClient) -> None:
    response = client.post("/api/v1/resources/match", json={"need_tag_codes": "meal_difficulty"})
    assert response.status_code == 422


def test_create_case_note_hides_raw_content_by_default(client: TestClient) -> None:
    raw = "Synthetic visit note for C-0001."
    response = client.post("/api/v1/cases/CASE-0001/notes", json={"note_type": "visit", "content_raw": raw}, headers=auth_headers(client))
    assert response.status_code == 200
    payload = response.json()
    assert payload["note"]["content_raw"] == "[REDACTED_RAW_CONTENT]"
    assert payload["note"]["content_display"] == raw
    assert payload["note"]["content_clean"] == raw
    assert payload["note"]["source"] == "human"


def test_created_note_is_visible_in_case_timeline(client: TestClient) -> None:
    raw = "Timeline visibility note for C-0001."
    create_response = client.post("/api/v1/cases/CASE-0001/notes", json={"note_type": "visit", "content_raw": raw}, headers=auth_headers(client))
    assert create_response.status_code == 200
    note_id = create_response.json()["note"]["id"]
    timeline_response = client.get("/api/v1/cases/CASE-0001/notes")
    assert timeline_response.status_code == 200
    assert note_id in {item["id"] for item in timeline_response.json()["items"]}


def test_create_case_note_rejects_blank_content(client: TestClient) -> None:
    response = client.post("/api/v1/cases/CASE-0001/notes", json={"note_type": "visit", "content_raw": ""}, headers=auth_headers(client))
    assert response.status_code == 422


def test_redactor_masks_long_digit_run(client: TestClient) -> None:
    raw = "demo 13800000000"
    response = client.post("/api/v1/cases/CASE-0001/notes", json={"note_type": "visit", "content_raw": raw}, headers=auth_headers(client))
    assert response.status_code == 200
    payload = response.json()
    assert "[REDACTED_PHONE]" in payload["note"]["content_clean"]
    assert payload["note"]["pii_detected"] is True


def test_create_service_goal(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cases/CASE-0001/goals",
        json={"title": "建立稳定餐食支持", "target_state": "完成助餐资源核实并形成跟进安排"},
        headers=auth_headers(client),
    )
    assert response.status_code == 200
    goal = response.json()["goal"]
    assert goal["case_id"] == "CASE-0001"
    assert goal["status"] == "not_started"
    list_response = client.get("/api/v1/cases/CASE-0001/goals")
    assert list_response.status_code == 200
    assert goal["id"] in {item["id"] for item in list_response.json()["items"]}


def test_create_resource_link_candidate(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cases/CASE-0001/referrals",
        json={"resource_code": "R-001", "agreement_status": "none", "notes": "candidate only"},
        headers=auth_headers(client),
    )
    assert response.status_code == 200
    referral = response.json()["referral"]
    assert referral["resource_code"] == "R-001"
    assert referral["status"] == "to_verify"
    assert referral["agreement_status"] == "none"


def test_resource_link_requires_agreement_before_referred(client: TestClient) -> None:
    headers = auth_headers(client)
    create_response = client.post("/api/v1/cases/CASE-0001/referrals", json={"resource_code": "R-003", "agreement_status": "none"}, headers=headers)
    assert create_response.status_code == 200
    referral_id = create_response.json()["referral"]["id"]

    blocked_response = client.patch(f"/api/v1/cases/CASE-0001/referrals/{referral_id}/status", json={"status": "referred"}, headers=headers)
    assert blocked_response.status_code == 409

    contacted_response = client.patch(f"/api/v1/cases/CASE-0001/referrals/{referral_id}/status", json={"status": "contacted"}, headers=headers)
    assert contacted_response.status_code == 200

    allowed_response = client.patch(
        f"/api/v1/cases/CASE-0001/referrals/{referral_id}/status",
        json={"status": "referred", "agreement_status": "verbal"},
        headers=headers,
    )
    assert allowed_response.status_code == 200
    assert allowed_response.json()["referral"]["status"] == "referred"


def test_unified_timeline_contains_manual_events(client: TestClient) -> None:
    headers = auth_headers(client)
    client.post("/api/v1/cases/CASE-0001/goals", json={"title": "timeline goal", "target_state": "visible in unified timeline"}, headers=headers)
    client.post("/api/v1/cases/CASE-0001/referrals", json={"resource_code": "R-005", "agreement_status": "none"}, headers=headers)
    timeline_response = client.get("/api/v1/cases/CASE-0001/timeline")
    assert timeline_response.status_code == 200
    kinds = {item["kind"] for item in timeline_response.json()["items"]}
    assert "note" in kinds
    assert "goal" in kinds
    assert "resource_link" in kinds
    assert "audit" in kinds


def test_prompt_registry_rejects_unknown_provider() -> None:
    prompt = get_prompt_spec("intake-v0.1.7")
    with pytest.raises(ValueError, match="provider_not_enabled"):
        generate_with_provider("external", prompt, "clean text")


def test_redaction_gateway_reports_masked_sensitive_content() -> None:
    result = run_redaction_gate("demo 手机号 13800000000")
    assert result.report.blocked is False
    assert result.report.pii_hit_count >= 1
    assert "[REDACTED_PHONE]" in result.clean_text


def test_golden_fixture_for_mock_intake_provider() -> None:
    fixture_path = Path(__file__).parents[1] / "app" / "ai" / "fixtures" / "c0001_intake_golden.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    output = generate_intake_draft(fixture["input"]["clean_text"]).model_dump()
    for field, expected_values in fixture["expected_contains"].items():
        for expected in expected_values:
            assert expected in output[field]


def test_ai_intake_output_is_draft_only(client: TestClient) -> None:
    note_id = client.get("/api/v1/cases/CASE-0001/notes").json()["items"][0]["id"]
    response = client.post("/api/v1/cases/CASE-0001/ai/intake", json={"note_id": note_id}, headers=auth_headers(client))
    assert response.status_code == 200
    payload = response.json()
    output = payload["output"]
    assert payload["provider"] == "mock"
    assert payload["prompt_version"] == "intake-v0.1.7"
    assert payload["redaction"]["blocked"] is False
    assert output["review_status"] == "pending"
    assert output["output_type"] == "intake"
    assert "needs" in output["parsed_output"]


def test_ai_output_review_updates_review_status_only(client: TestClient) -> None:
    headers = auth_headers(client)
    note_id = client.get("/api/v1/cases/CASE-0001/notes").json()["items"][0]["id"]
    output = client.post("/api/v1/cases/CASE-0001/ai/intake", json={"note_id": note_id}, headers=headers).json()["output"]
    review_response = client.patch(
        f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/review",
        json={"review_status": "accepted", "reviewer_notes": "manual review completed"},
        headers=headers,
    )
    assert review_response.status_code == 200
    reviewed_output = review_response.json()["output"]
    assert reviewed_output["review_status"] == "accepted"
    assert reviewed_output["reviewed_by"] == "demo_social_worker"
    assert "ai_outputs" not in client.get("/api/v1/cases/CASE-0001").json()["case"]


def test_apply_preview_requires_reviewed_ai_output(client: TestClient) -> None:
    headers = auth_headers(client)
    note_id = client.get("/api/v1/cases/CASE-0001/notes").json()["items"][0]["id"]
    output = client.post("/api/v1/cases/CASE-0001/ai/intake", json={"note_id": note_id}, headers=headers).json()["output"]
    blocked = client.post(f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/apply-preview", headers=headers)
    assert blocked.status_code == 409
    client.patch(f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/review", json={"review_status": "accepted"}, headers=headers)
    allowed = client.post(f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/apply-preview", headers=headers)
    assert allowed.status_code == 200
    preview = allowed.json()["preview"]
    assert preview["will_write_formal_fields"] is False
    assert preview["requires_explicit_apply_action"] is True


def test_explicit_apply_to_assessment_requires_review_and_responsibility(client: TestClient) -> None:
    headers = auth_headers(client)
    note_id = client.get("/api/v1/cases/CASE-0001/notes").json()["items"][0]["id"]
    output = client.post("/api/v1/cases/CASE-0001/ai/intake", json={"note_id": note_id}, headers=headers).json()["output"]
    blocked_pending = client.post(f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/apply-to-assessment", json={"reviewer_responsibility_accepted": True}, headers=headers)
    assert blocked_pending.status_code == 409
    client.patch(f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/review", json={"review_status": "accepted"}, headers=headers)
    blocked_responsibility = client.post(f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/apply-to-assessment", json={"reviewer_responsibility_accepted": False}, headers=headers)
    assert blocked_responsibility.status_code == 409
    applied = client.post(f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/apply-to-assessment", json={"reviewer_responsibility_accepted": True, "reviewer_id": "ignored_client_value"}, headers=headers)
    assert applied.status_code == 200
    assessment = applied.json()["assessment"]
    assert assessment["source_ai_output_id"] == output["id"]
    assert assessment["reviewer_id"] == "demo_social_worker"
    assert assessment["reviewer_responsibility_accepted"] is True
    assert assessment["provider"] == "mock"
    assert assessment["prompt_version"] == "intake-v0.1.7"
    assessments = client.get("/api/v1/cases/CASE-0001/assessments").json()["items"]
    assert assessment["id"] in {item["id"] for item in assessments}


def test_timeline_contains_assessment_and_apply_audit(client: TestClient) -> None:
    headers = auth_headers(client)
    note_id = client.get("/api/v1/cases/CASE-0001/notes").json()["items"][0]["id"]
    output = client.post("/api/v1/cases/CASE-0001/ai/intake", json={"note_id": note_id}, headers=headers).json()["output"]
    client.patch(f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/review", json={"review_status": "accepted"}, headers=headers)
    client.post(f"/api/v1/cases/CASE-0001/ai/outputs/{output['id']}/apply-to-assessment", json={"reviewer_responsibility_accepted": True}, headers=headers)
    timeline_response = client.get("/api/v1/cases/CASE-0001/timeline")
    assert timeline_response.status_code == 200
    items = timeline_response.json()["items"]
    kinds = {item["kind"] for item in items}
    audit_titles = {item["title"] for item in items if item["kind"] == "audit"}
    assert "assessment" in kinds
    assert "ai.output.applied_to_assessment" in audit_titles
