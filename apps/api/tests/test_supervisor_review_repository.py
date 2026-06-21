from app.db.service_plan_repository import create_intervention, create_service_plan
from app.db.supervisor_review_repository import build_closure_readiness, create_review, list_reviews
from app.db.session import SessionLocal


def test_supervisor_review_repository_builds_readiness_and_review() -> None:
    with SessionLocal() as db:
        plan = create_service_plan(
            db,
            "CASE-0001",
            {"title": "Closure readiness plan", "plan_status": "active", "plan_data": {"focus": "support"}},
            "demo_social_worker",
            1,
        )
        create_intervention(
            db,
            "CASE-0001",
            {"plan_id": plan["id"], "intervention_type": "followup", "narrative": "Manual follow-up for closure readiness."},
            "demo_social_worker",
            1,
        )
        readiness = build_closure_readiness(db, "CASE-0001", 1)
        review = create_review(db, "CASE-0001", {"decision": "continue_service", "note": "Continue service and review later."}, "demo_supervisor", 1)
        listed = list_reviews(db, "CASE-0001", 1)

        assert readiness["manual_only"] is True
        assert "plan_count" in readiness["evidence_summary"]
        assert review["reviewed_by"] == "demo_supervisor"
        assert review["id"] in {item["id"] for item in listed}
