from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.assessment_revision_repository import create_assessment_correction, list_assessment_corrections
from app.db.persistent_repository import get_case, list_case_assessments
from app.db.session import get_db

router = APIRouter(prefix="/cases/{case_id}/assessments", tags=["assessments"])


class AssessmentCorrectionRequest(BaseModel):
    reviewer_id: str = Field(default="demo_supervisor", min_length=1, max_length=120)
    reviewer_role: str = Field(default="supervisor", pattern="^(worker|supervisor|admin)$")
    reason: str = Field(min_length=1, max_length=1000)
    correction_data: dict = Field(default_factory=dict)


@router.get("")
def index(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_case_assessments(db, case_id)}


@router.get("/{assessment_id}/corrections")
def corrections(case_id: str, assessment_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_assessment_corrections(db, case_id, assessment_id)}


@router.post("/{assessment_id}/corrections")
def create_correction(case_id: str, assessment_id: str, payload: AssessmentCorrectionRequest, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        correction = create_assessment_correction(db, case_id, assessment_id, payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"correction": correction}
