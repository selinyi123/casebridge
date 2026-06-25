from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.main import app


def headers(username: str, role: str) -> dict[str, str]:
    token = create_access_token(subject=username, role=role, organization_id=1)
    return {"Authorization": f"Bearer {token}"}


def test_explicit_close_requires_approved_draft_and_confirmation() -> None:
    with TestClient(app) as client:
        worker = headers("demo_social_worker", "social_worker")
        supervisor = headers("demo_supervisor", "supervisor")
        created = client.post(
            "/api/v1/cases/CASE-0001/goals/closure-drafts",
            json={"closure_reason": "Manual close route draft."},
            headers=worker,
        )
        assert created.status_code == 200
        draft_id = created.json()["draft"]["id"]

        missing_confirmation = client.post(
            "/api/v1/cases/CASE-0001/closure-state/close",
            json={"closure_draft_id": draft_id, "confirm_case_closure": False, "responsibility_accepted": True},
            headers=supervisor,
        )
        assert missing_confirmation.status_code == 409

        not_approved = client.post(
            "/api/v1/cases/CASE-0001/closure-state/close",
            json={"closure_draft_id": draft_id, "confirm_case_closure": True, "responsibility_accepted": True},
            headers=supervisor,
        )
        assert not_approved.status_code == 409

        reviewed = client.post(
            f"/api/v1/cases/CASE-0001/goals/closure-drafts/{draft_id}/review",
            json={"decision": "approved"},
            headers=supervisor,
        )
        assert reviewed.status_code == 200

        closed = client.post(
            "/api/v1/cases/CASE-0001/closure-state/close",
            json={"closure_draft_id": draft_id, "confirm_case_closure": True, "responsibility_accepted": True},
            headers=supervisor,
        )
        assert closed.status_code == 200
        assert closed.json()["case_status_changed"] is True
        assert closed.json()["case"]["status"] == "closed"
