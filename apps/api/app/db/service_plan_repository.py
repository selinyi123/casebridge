from itertools import count
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, CaseAssessment, ServiceGoal, ServiceOutcome, model_to_dict
from app.db.service_plan_models import ServiceIntervention, ServicePlan

_plan_counter = count(1)
_intervention_counter = count(1)


def _next_id(prefix: str, counter: count, model: type, db: Session) -> str:
    identifier = f"{prefix}-{next(counter):04d}"
    while db.get(model, identifier):
        identifier = f"{prefix}-{next(counter):04d}"
    return identifier


def list_service_plans(db: Session, case_id: str, organization_id: int = 1) -> list[dict[str, Any]]:
    stmt = select(ServicePlan).where(ServicePlan.organization_id == organization_id, ServicePlan.case_id == case_id).order_by(ServicePlan.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_service_plan(db: Session, case_id: str, payload: dict[str, Any], actor: str, organization_id: int = 1) -> dict[str, Any]:
    assessment_id = payload.get("assessment_id")
    if assessment_id:
        assessment = db.scalar(select(CaseAssessment).where(CaseAssessment.id == assessment_id, CaseAssessment.organization_id == organization_id))
        if not assessment or assessment.case_id != case_id:
            raise ValueError("assessment_not_found")
    plan = ServicePlan(
        id=_next_id("PLAN", _plan_counter, ServicePlan, db),
        organization_id=organization_id,
        case_id=case_id,
        assessment_id=assessment_id,
        title=payload.get("title", ""),
        plan_status=payload.get("plan_status", "draft"),
        plan_data=payload.get("plan_data", {}),
        created_by=actor,
    )
    db.add(plan)
    db.add(AuditEvent(organization_id=organization_id, case_id=case_id, event_type="service_plan.created", entity_type="service_plan", entity_id=plan.id, actor=actor, payload={"assessment_id": assessment_id, "plan_status": plan.plan_status}))
    db.commit()
    db.refresh(plan)
    return model_to_dict(plan)


def list_interventions(db: Session, case_id: str, organization_id: int = 1) -> list[dict[str, Any]]:
    stmt = select(ServiceIntervention).where(ServiceIntervention.organization_id == organization_id, ServiceIntervention.case_id == case_id).order_by(ServiceIntervention.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_intervention(db: Session, case_id: str, payload: dict[str, Any], actor: str, organization_id: int = 1) -> dict[str, Any]:
    plan = db.scalar(select(ServicePlan).where(ServicePlan.id == payload.get("plan_id"), ServicePlan.organization_id == organization_id))
    if not plan or plan.case_id != case_id:
        raise ValueError("plan_not_found")
    goal_id = payload.get("goal_id")
    if goal_id:
        goal = db.scalar(select(ServiceGoal).where(ServiceGoal.id == goal_id, ServiceGoal.organization_id == organization_id))
        if not goal or goal.case_id != case_id:
            raise ValueError("goal_not_found")
    intervention = ServiceIntervention(
        id=_next_id("INTV", _intervention_counter, ServiceIntervention, db),
        organization_id=organization_id,
        case_id=case_id,
        plan_id=plan.id,
        goal_id=goal_id,
        intervention_type=payload.get("intervention_type", "followup"),
        narrative=payload.get("narrative", ""),
        evidence=payload.get("evidence"),
        recorded_by=actor,
    )
    db.add(intervention)
    db.add(AuditEvent(organization_id=organization_id, case_id=case_id, event_type="intervention.created", entity_type="service_intervention", entity_id=intervention.id, actor=actor, payload={"plan_id": plan.id, "goal_id": goal_id}))
    db.commit()
    db.refresh(intervention)
    return model_to_dict(intervention)


def build_evidence_chain(db: Session, case_id: str, organization_id: int = 1) -> dict[str, Any]:
    plans = list_service_plans(db, case_id, organization_id)
    interventions = list_interventions(db, case_id, organization_id)
    outcomes_stmt = select(ServiceOutcome).where(ServiceOutcome.organization_id == organization_id, ServiceOutcome.case_id == case_id).order_by(ServiceOutcome.created_at)
    outcomes = [model_to_dict(row) for row in db.scalars(outcomes_stmt).all()]
    events = []
    for plan in plans:
        events.append({"kind": "service_plan", "id": plan["id"], "at": plan["created_at"], "payload": plan})
    for item in interventions:
        events.append({"kind": "service_intervention", "id": item["id"], "at": item["created_at"], "payload": item})
    for outcome in outcomes:
        events.append({"kind": "outcome", "id": outcome["id"], "at": outcome["created_at"], "payload": outcome})
    return {"case_id": case_id, "plans": plans, "interventions": interventions, "outcomes": outcomes, "events": sorted(events, key=lambda item: item["at"]), "manual_only": True}
