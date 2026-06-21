from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.assessment_catalog import get_schema
from app.core.auth import RequireCaseWriter
from app.db.outcome_repository import create_service_outcome, list_service_outcomes
from app.db.persistent_repository import get_case
from app.db.session import get_db
from app.schemas import CreateServiceOutcomeRequest

router = APIRouter(prefix="/cases/{case_id}/outcomes", tags=["outcomes"])


@router.get("/schema/{schema_id}")
def schema(case_id: str, schema_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        return {"schema": get_schema(schema_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("")
def index(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_service_outcomes(db, case_id)}


@router.post("")
def create(case_id: str, payload: CreateServiceOutcomeRequest, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        outcome = create_service_outcome(db, case_id, payload.model_dump(), actor=current_user.username)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"outcome": outcome}
