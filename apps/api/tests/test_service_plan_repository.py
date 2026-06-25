from sqlalchemy.orm import Session

from app.db.service_plan_repository import build_evidence_chain, create_intervention, create_service_plan
from tests.factories import seed_route_case


def test_service_plan_repository_builds_manual_evidence_chain(test_session: Session) -> None:
    case_id = "CASE-PLAN-REPO"
    seed_route_case(case_id, status="open", stage="service", db=test_session)
    plan = create_service_plan(
        test_session,
        case_id,
        {"title": "Manual plan", "plan_status": "active", "plan_data": {"focus": "daily"}},
        "demo_social_worker",
        1,
    )
    intervention = create_intervention(
        test_session,
        case_id,
        {"plan_id": plan["id"], "intervention_type": "followup", "narrative": "Manual follow-up."},
        "demo_social_worker",
        1,
    )
    chain = build_evidence_chain(test_session, case_id, 1)
    event_ids = {item["id"] for item in chain["events"]}
    event_kinds = {item["kind"] for item in chain["events"]}

    assert chain["manual_only"] is True
    assert plan["id"] in {item["id"] for item in chain["plans"]}
    assert intervention["id"] in {item["id"] for item in chain["interventions"]}
    assert plan["id"] in event_ids
    assert intervention["id"] in event_ids
    assert "service_plan" in event_kinds
    assert "service_intervention" in event_kinds
