from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import RequireAdmin, RequireCaseWriter
from app.core.privacy import redact_text
from app.db.persistent_repository import create_case_note, get_case, list_case_notes, list_cases, record_audit_event
from app.db.session import get_db
from app.schemas import CreateCaseNoteRequest

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("")
def index(db: Session = Depends(get_db)) -> dict:
    return {"items": list_cases(db)}


@router.get("/{case_id}")
def show(case_id: str, db: Session = Depends(get_db)) -> dict:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"case": case, "notes": list_case_notes(db, case_id)}


@router.get("/{case_id}/notes")
def notes(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_case_notes(db, case_id)}


@router.get("/{case_id}/notes/raw")
def raw_notes(case_id: str, current_user: RequireAdmin, db: Session = Depends(get_db)) -> dict:
    organization_id = current_user.organization_id
    if not get_case(db, case_id, organization_id=organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    record_audit_event(
        db,
        case_id=case_id,
        event_type="note.raw_viewed",
        entity_type="case_note",
        entity_id="*",
        payload={"reason": "admin_raw_note_access"},
        actor=current_user.username,
        organization_id=organization_id,
    )
    db.commit()
    return {"items": list_case_notes(db, case_id, include_raw=True, organization_id=organization_id), "viewed_by": current_user.username}


@router.post("/{case_id}/notes")
def create_note(case_id: str, payload: CreateCaseNoteRequest, current_user: RequireCaseWriter, db: Session = Depends(get_db)) -> dict:
    organization_id = current_user.organization_id
    if not get_case(db, case_id, organization_id=organization_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    raw = payload.content_raw.strip()
    redacted = redact_text(raw)
    note = create_case_note(
        db=db,
        case_id=case_id,
        payload={
            "note_type": payload.note_type,
            "content_raw": raw,
            "occurred_at": payload.occurred_at,
        },
        content_clean=redacted.clean_text,
        pii_detected=bool(redacted.pii_hits),
        actor=current_user.username,
        organization_id=organization_id,
    )
    return {
        "note": note,
        "redaction": {
            "pii_hits": redacted.pii_hits,
            "is_safe_for_model": redacted.is_safe_for_model,
        },
    }
