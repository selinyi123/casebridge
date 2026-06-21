from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.roles import CORRECTION_ROLES, require_role
from app.db.models import AuditEvent, CaseAssessment, model_to_dict


def list_assessment_corrections(db: Session, case_id: str, assessment_id: str) -> list[dict[str, Any]]:
    stmt = (
        select(AuditEvent)
        .where(AuditEvent.case_id == case_id)
        .where(AuditEvent.entity_type == "case_assessment")
        .where(AuditEvent.entity_id == assessment_id)
        .where(AuditEvent.event_type == "assessment.corrected")
        .order_by(AuditEvent.created_at)
    )
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_assessment_correction(db: Session, case_id: str, assessment_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    role = payload.get("reviewer_role", "worker")
    require_role(role, CORRECTION_ROLES)
    assessment = db.get(CaseAssessment, assessment_id)
    if not assessment or assessment.case_id != case_id:
        raise ValueError("assessment_not_found")
    event = AuditEvent(
        case_id=case_id,
        event_type="assessment.corrected",
        entity_type="case_assessment",
        entity_id=assessment_id,
        actor=payload.get("reviewer_id", "demo_supervisor"),
        payload={
            "reviewer_role": role,
            "reason": payload.get("reason", "manual_correction"),
            "correction_data": payload.get("correction_data", {}),
            "source_assessment_id": assessment_id,
        },
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return model_to_dict(event)
