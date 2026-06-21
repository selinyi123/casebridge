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


@router.get("/report")
def report(case_id: str, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    organization_id = current_user.organization_id
    if not get_case(db, case_id, organization_id=organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    outcomes = list_service_outcomes(db, case_id, organization_id=organization_id)
    scores = [item["gas_score"] for item in outcomes if item.get("gas_score") is not None]
    return {
        "case_id": case_id,
        "outcome_count": len(outcomes),
        "gas_score_count": len(scores),
        "latest_gas_score": scores[-1] if scores else None,
        "manual_only": True,
        "items": outcomes,
    }


@router.get("")
def index(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_service_outcomes(db, case_id)}


@router.post("")
def create(case_id: str, payload: CreateServiceOutcomeRequest, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    organization_id = current_user.organization_id
    if not get_case(db, case_id, organization_id=organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        outcome = create_service_outcome(db, case_id, payload.model_dump(), actor=current_user.username, organization_id=organization_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"outcome": outcome}
