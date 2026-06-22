from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.main import app


def headers(username: str, role: str) -> dict[str, str]:
    token = create_access_token(subject=username, role=role, organization_id=1)
    return {"Authorization": f"Bearer {token}"}


def test_closure_draft_route_does_not_close_case() -> None:
    with TestClient(app) as client:
        worker = headers("demo_social_worker", "social_worker")
        supervisor = headers("demo_supervisor", "supervisor")

        report = client.get("/api/v1/cases/CASE-0001/goals/closure-report", headers=worker)
        assert report.status_code == 200
        assert report.json()["auto_close"] is False

        created = client.post(
            "/api/v1/cases/CASE-0001/goals/closure-drafts",
            json={"closure_reason": "Manual route closure draft."},
            headers=worker,
        )
        assert created.status_code == 200
        draft_id = created.json()["draft"]["id"]

        blocked = client.post(
            f"/api/v1/cases/CASE-0001/goals/closure-drafts/{draft_id}/review",
            json={"decision": "approved"},
            headers=worker,
        )
        assert blocked.status_code == 403

        reviewed = client.post(
            f"/api/v1/cases/CASE-0001/goals/closure-drafts/{draft_id}/review",
            json={"decision": "approved"},
            headers=supervisor,
        )
        assert reviewed.status_code == 200
        assert reviewed.json()["case_status_changed"] is False
        assert reviewed.json()["draft"]["draft_status"] == "approved"
