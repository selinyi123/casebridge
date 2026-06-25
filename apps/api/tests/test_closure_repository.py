from sqlalchemy.orm import Session

from app.db.closure_repository import approve_closure_draft, build_closure_report, create_closure_draft, list_closure_drafts
from app.db.persistent_repository import get_case
from app.db.service_plan_repository import create_intervention, create_service_plan
from tests.factories import seed_route_case


def test_closure_draft_review_does_not_close_case(test_session: Session) -> None:
    case_id = "CASE-CLOSURE-REPO"
    seed_route_case(case_id, status="open", stage="service", db=test_session)
    plan = create_service_plan(
        test_session,
        case_id,
        {"title": "Closure plan", "plan_status": "active", "plan_data": {"focus": "close"}},
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
    report = build_closure_report(test_session, case_id, 1)
    draft = create_closure_draft(test_session, case_id, {"closure_reason": "Manual closure draft."}, "demo_social_worker", 1)
    reviewed = approve_closure_draft(test_session, case_id, draft["id"], "approved", "demo_supervisor", 1)
    listed = list_closure_drafts(test_session, case_id, 1)
    case = get_case(test_session, case_id, organization_id=1)

    assert report["manual_only"] is True
    assert report["auto_close"] is False
    assert draft["draft_status"] == "draft"
    assert reviewed["draft_status"] == "approved"
    assert reviewed["approved_by"] == "demo_supervisor"
    assert draft["id"] in {item["id"] for item in listed}
    assert case["status"] == "open"
