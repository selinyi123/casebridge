from app.db.service_plan_repository import build_evidence_chain, create_intervention, create_service_plan
from app.db.session import SessionLocal


def test_service_plan_repository_builds_manual_evidence_chain() -> None:
    with SessionLocal() as db:
        plan = create_service_plan(
            db,
            "CASE-0001",
            {"title": "Manual support plan", "plan_status": "active", "plan_data": {"focus": "meal support"}},
            "demo_social_worker",
            1,
        )
        intervention = create_intervention(
            db,
            "CASE-0001",
            {"plan_id": plan["id"], "intervention_type": "followup", "narrative": "Manual follow-up completed.", "evidence": "Demo evidence."},
            "demo_social_worker",
            1,
        )
        chain = build_evidence_chain(db, "CASE-0001", 1)

        assert chain["manual_only"] is True
        assert plan["id"] in {item["id"] for item in chain["plans"]}
        assert intervention["id"] in {item["id"] for item in chain["interventions"]}
