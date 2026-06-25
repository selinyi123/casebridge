from sqlalchemy.orm import Session

from app.db.service_plan_repository import create_intervention, create_service_plan
from app.db.supervisor_review_repository import build_closure_readiness, create_review, list_reviews
from tests.factories import seed_route_case


def test_supervisor_review_repository_builds_readiness_and_review(test_session: Session) -> None:
    case_id = "CASE-REVIEW-REPO"
    seed_route_case(case_id, status="open", stage="service", db=test_session)
    plan = create_service_plan(
        test_session,
        case_id,
        {"title": "Review plan", "plan_status": "active", "plan_data": {"focus": "review"}},
        "demo_social_worker",
        1,
    )
    create_intervention(
        test_session,
        case_id,
        {"plan_id": plan["id"], "intervention_type": "followup", "narrative": "Manual follow-up."},
        "demo_social_worker",
        1,
    )
    readiness = build_closure_readiness(test_session, case_id, 1)
    review = create_review(test_session, case_id, {"decision": "continue_service", "note": "Continue service."}, "demo_supervisor", 1)
    listed = list_reviews(test_session, case_id, 1)

    assert readiness["manual_only"] is True
    assert "plan_count" in readiness["evidence_summary"]
    assert review["reviewed_by"] == "demo_supervisor"
    assert review["id"] in {item["id"] for item in listed}
