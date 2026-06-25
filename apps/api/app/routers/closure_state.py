from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import RequireSupervisorReviewer
from app.db.closure_repository import close_case_from_approved_draft
from app.db.persistent_repository import get_case
from app.db.session import get_db

router = APIRouter(prefix="/cases/{case_id}/closure-state", tags=["closure-state"])


class ExplicitCloseRequest(BaseModel):
    closure_draft_id: str
    confirm_case_closure: bool
    responsibility_accepted: bool


@router.post("/close")
def close_case(case_id: str, payload: ExplicitCloseRequest, current_user: RequireSupervisorReviewer, db: Session = Depends(get_db)) -> dict:
    if not payload.confirm_case_closure or not payload.responsibility_accepted:
        raise HTTPException(status_code=409, detail="explicit_confirmation_required")
    if not get_case(db, case_id, organization_id=current_user.organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        case = close_case_from_approved_draft(db, case_id, payload.closure_draft_id, current_user.username, current_user.organization_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"case": case, "case_status_changed": True, "manual_only": True}
