from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import RequireCaseWriter
from app.db.persistent_repository import (
    create_referral,
    get_case,
    get_resource,
    list_referrals,
    update_referral_status,
)
from app.db.session import get_db
from app.schemas import CreateReferralRequest, UpdateReferralStatusRequest

router = APIRouter(prefix="/cases/{case_id}/referrals", tags=["referrals"])


@router.get("")
def index(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_referrals(db, case_id)}


@router.post("")
def create(case_id: str, payload: CreateReferralRequest, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    if not get_resource(db, payload.resource_code):
        raise HTTPException(status_code=404, detail="resource_not_found")
    referral = create_referral(db, case_id, payload.model_dump(), actor=current_user.username)
    return {"referral": referral}


@router.patch("/{referral_id}/status")
def update_status(case_id: str, referral_id: str, payload: UpdateReferralStatusRequest, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        referral = update_referral_status(
            db=db,
            case_id=case_id,
            referral_id=referral_id,
            status=payload.status,
            agreement_status=payload.agreement_status,
            actor=current_user.username,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not referral:
        raise HTTPException(status_code=404, detail="referral_not_found")
    return {"referral": referral}
