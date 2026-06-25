from fastapi.testclient import TestClient

from app.core.auth import create_access_token
from app.db.models import CaseRecord, Client
from app.db.session import SessionLocal
from app.main import app


def headers(username: str, role: str) -> dict[str, str]:
    token = create_access_token(subject=username, role=role, organization_id=1)
    return {"Authorization": f"Bearer {token}"}


def seed_closed_case(case_id: str) -> None:
    with SessionLocal() as db:
        db.merge(Client(code="CLIENT-REOPEN-TEST", organization_id=1, display_name="Reopen Test", age=80, community="Test", client_type="demo", primary_concern="Test"))
        db.merge(CaseRecord(id=case_id, organization_id=1, client_code="CLIENT-REOPEN-TEST", title="Reopen route test", stage="closed", status="closed"))
        db.commit()


def test_explicit_reopen_requires_approved_request_and_confirmation() -> None:
    case_id = "CASE-REOPEN-ROUTE"
    seed_closed_case(case_id)
    with TestClient(app) as client:
        worker = headers("demo_social_worker", "social_worker")
        supervisor = headers("demo_supervisor", "supervisor")
        created = client.post(
            f"/api/v1/cases/{case_id}/reopen-state/requests",
            json={"reopen_reason": "Manual reopen request."},
            headers=worker,
        )
        assert created.status_code == 200
        request_id = created.json()["request"]["id"]

        missing_confirmation = client.post(
            f"/api/v1/cases/{case_id}/reopen-state/reopen",
            json={"reopen_request_id": request_id, "confirm_case_reopen": False, "responsibility_accepted": True},
            headers=supervisor,
        )
        assert missing_confirmation.status_code == 409

        not_approved = client.post(
            f"/api/v1/cases/{case_id}/reopen-state/reopen",
            json={"reopen_request_id": request_id, "confirm_case_reopen": True, "responsibility_accepted": True},
            headers=supervisor,
        )
        assert not_approved.status_code == 409

        reviewed = client.post(
            f"/api/v1/cases/{case_id}/reopen-state/requests/{request_id}/review",
            json={"decision": "approved"},
            headers=supervisor,
        )
        assert reviewed.status_code == 200
        assert reviewed.json()["case_status_changed"] is False

        reopened = client.post(
            f"/api/v1/cases/{case_id}/reopen-state/reopen",
            json={"reopen_request_id": request_id, "confirm_case_reopen": True, "responsibility_accepted": True},
            headers=supervisor,
        )
        assert reopened.status_code == 200
        assert reopened.json()["case_status_changed"] is True
        assert reopened.json()["case"]["status"] == "open"
        assert reopened.json()["case"]["stage"] == "reopened"
