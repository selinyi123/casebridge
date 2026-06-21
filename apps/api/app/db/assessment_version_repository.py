from itertools import count
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import CaseAssessment, CaseAssessmentVersion, model_to_dict

_counter = count(1)


def _next_id(db: Session) -> str:
    identifier = f"ASSESSV-{next(_counter):04d}"
    while db.get(CaseAssessmentVersion, identifier):
        identifier = f"ASSESSV-{next(_counter):04d}"
    return identifier


def list_versions(db: Session, case_id: str, assessment_id: str, organization_id: int) -> list[dict[str, Any]]:
    stmt = (
        select(CaseAssessmentVersion)
        .where(CaseAssessmentVersion.organization_id == organization_id)
        .where(CaseAssessmentVersion.case_id == case_id)
        .where(CaseAssessmentVersion.assessment_id == assessment_id)
        .order_by(CaseAssessmentVersion.version_number)
    )
    return [model_to_dict(row) for row in db.scalars(stmt).all()]


def create_version(db: Session, case_id: str, assessment_id: str, data: dict[str, Any], reason: str, actor: str, organization_id: int) -> dict[str, Any]:
    assessment = db.scalar(select(CaseAssessment).where(CaseAssessment.id == assessment_id, CaseAssessment.organization_id == organization_id))
    if not assessment or assessment.case_id != case_id:
        raise ValueError("assessment_not_found")
    current_max = db.scalar(
        select(func.max(CaseAssessmentVersion.version_number)).where(
            CaseAssessmentVersion.organization_id == organization_id,
            CaseAssessmentVersion.assessment_id == assessment_id,
        )
    )
    version = CaseAssessmentVersion(
        id=_next_id(db),
        organization_id=organization_id,
        case_id=case_id,
        assessment_id=assessment_id,
        version_number=int(current_max or 0) + 1,
        version_data=data,
        reason=reason,
        created_by=actor,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return model_to_dict(version)
