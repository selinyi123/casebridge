from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import RequireAdmin, RequireCaseWriter
from app.db.assessment_revision_repository import create_assessment_correction, list_assessment_corrections
from app.db.models import User
from app.db.persistent_repository import get_case, list_case_assessments
from app.db.session import get_db

router = APIRouter(prefix="/cases/{case_id}/assessments", tags=["assessments"])


class AssessmentCorrectionRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)
    correction_data: dict = Field(default_factory=dict)


@router.get("")
def index(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_case_assessments(db, case_id)}


@router.get("/{assessment_id}/corrections")
def corrections(case_id: str, assessment_id: str, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_assessment_corrections(db, case_id, assessment_id)}


@router.post("/{assessment_id}/corrections")
def create_correction(case_id: str, assessment_id: str, payload: AssessmentCorrectionRequest, current_user: RequireAdmin, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        correction = create_assessment_correction(
            db,
            case_id,
            assessment_id,
            {
                "reviewer_id": current_user.username,
                "reviewer_role": current_user.role,
                "reason": payload.reason,
                "correction_data": payload.correction_data,
            },
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"correction": correction}
