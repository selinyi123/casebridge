from app.db.closure_repository import approve_closure_draft, build_closure_report, create_closure_draft, list_closure_drafts
from app.db.persistent_repository import get_case
from app.db.service_plan_repository import create_intervention, create_service_plan
from app.db.session import SessionLocal


def test_closure_draft_review_does_not_close_case() -> None:
    with SessionLocal() as db:
        plan = create_service_plan(
            db,
            "CASE-0001",
            {"title": "Closure draft plan", "plan_status": "active", "plan_data": {"focus": "wrap up"}},
            "demo_social_worker",
            1,
        )
        create_intervention(
            db,
            "CASE-0001",
            {"plan_id": plan["id"], "intervention_type": "followup", "narrative": "Manual closure preparation follow-up."},
            "demo_social_worker",
            1,
        )
        report = build_closure_report(db, "CASE-0001", 1)
        draft = create_closure_draft(db, "CASE-0001", {"closure_reason": "Manual closure draft."}, "demo_social_worker", 1)
        reviewed = approve_closure_draft(db, "CASE-0001", draft["id"], "approved", "demo_supervisor", 1)
        listed = list_closure_drafts(db, "CASE-0001", 1)
        case = get_case(db, "CASE-0001", organization_id=1)

        assert report["manual_only"] is True
        assert report["auto_close"] is False
        assert draft["draft_status"] == "draft"
        assert reviewed["draft_status"] == "approved"
        assert reviewed["approved_by"] == "demo_supervisor"
        assert draft["id"] in {item["id"] for item in listed}
        assert case["status"] == "open"
