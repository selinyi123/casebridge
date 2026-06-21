from itertools import count
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, CaseAssessment, ServiceGoal, ServiceOutcome, model_to_dict

_outcome_counter = count(1)


def _next_id(prefix: str, counter: count, model: type, db: Session) -> str:
    identifier = f"{prefix}-{next(counter):04d}"
    while db.get(model, identifier):
        identifier = f"{prefix}-{next(counter):04d}"
    return identifier


def list_service_outcomes(db: Session, case_id: str) -> list[dict[str, Any]]:
    stmt = select(ServiceOutcome).where(ServiceOutcome.case_id == case_id).order_by(ServiceOutcome.created_at)
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_service_outcome(db: Session, case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    gas_score = payload.get("gas_score")
    if gas_score is not None and (gas_score < -2 or gas_score > 2):
        raise ValueError("gas_score_out_of_range")
    goal_id = payload.get("goal_id")
    assessment_id = payload.get("assessment_id")
    if goal_id and not db.get(ServiceGoal, goal_id):
        raise ValueError("goal_not_found")
    if assessment_id and not db.get(CaseAssessment, assessment_id):
        raise ValueError("assessment_not_found")
    outcome = ServiceOutcome(
        id=_next_id("OUTCOME", _outcome_counter, ServiceOutcome, db),
        case_id=case_id,
        goal_id=goal_id,
        assessment_id=assessment_id,
        outcome_type=payload.get("outcome_type", "goal_attainment"),
        gas_score=gas_score,
        narrative=payload.get("narrative", ""),
        evidence=payload.get("evidence"),
        recorded_by=payload.get("recorded_by", "demo_social_worker"),
    )
    db.add(outcome)
    db.add(AuditEvent(case_id=case_id, event_type="outcome.created", entity_type="service_outcome", entity_id=outcome.id, payload={"goal_id": goal_id, "assessment_id": assessment_id, "gas_score": gas_score}))
    db.commit()
    db.refresh(outcome)
    return model_to_dict(outcome)
