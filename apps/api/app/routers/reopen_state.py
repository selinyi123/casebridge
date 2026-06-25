from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import RequireCaseWriter, RequireSupervisorReviewer
from app.db.persistent_repository import get_case
from app.db.reopen_repository import create_reopen_request, list_reopen_requests, reopen_case_from_approved_request, review_reopen_request
from app.db.session import get_db

router = APIRouter(prefix="/cases/{case_id}/reopen-state", tags=["reopen-state"])


class CreateReopenRequest(BaseModel):
    reopen_reason: str = Field(min_length=1, max_length=3000)


class ReviewReopenRequest(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")


class ExplicitReopenRequest(BaseModel):
    reopen_request_id: str
    confirm_case_reopen: bool
    responsibility_accepted: bool


@router.get("/requests")
def requests(case_id: str, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_reopen_requests(db, case_id, current_user.organization_id)}


@router.post("/requests")
def create_request(case_id: str, payload: CreateReopenRequest, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    request = create_reopen_request(db, case_id, payload.model_dump(), current_user.username, current_user.organization_id)
    return {"request": request}


@router.post("/requests/{request_id}/review")
def review_request(case_id: str, request_id: str, payload: ReviewReopenRequest, current_user: RequireSupervisorReviewer, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        request = review_reopen_request(db, case_id, request_id, payload.decision, current_user.username, current_user.organization_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"request": request, "case_status_changed": False}


@router.post("/reopen")
def reopen_case(case_id: str, payload: ExplicitReopenRequest, current_user: RequireSupervisorReviewer, db: Session = Depends(get_db)) -> dict:
    if not payload.confirm_case_reopen or not payload.responsibility_accepted:
        raise HTTPException(status_code=409, detail="explicit_confirmation_required")
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        case = reopen_case_from_approved_request(db, case_id, payload.reopen_request_id, current_user.username, current_user.organization_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"case": case, "case_status_changed": True, "manual_only": True}
