from fastapi import APIRouter, HTTPException

from app.core.demo_store import create_case_note, get_case, list_case_notes, list_cases
from app.core.privacy import redact_text
from app.schemas import CreateCaseNoteRequest

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("")
def index() -> dict:
    return {"items": list_cases()}


@router.get("/{case_id}")
def show(case_id: str) -> dict:
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"case": case, "notes": list_case_notes(case_id)}


@router.get("/{case_id}/notes")
def notes(case_id: str) -> dict:
    if not get_case(case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_case_notes(case_id)}


@router.post("/{case_id}/notes")
def create_note(case_id: str, payload: CreateCaseNoteRequest) -> dict:
    if not get_case(case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    raw = payload.content_raw.strip()
    redacted = redact_text(raw)
    note = create_case_note(
        case_id=case_id,
        payload={
            "note_type": payload.note_type,
            "content_raw": raw,
            "occurred_at": payload.occurred_at,
        },
        content_clean=redacted.clean_text,
        pii_detected=bool(redacted.pii_hits),
    )
    return {
        "note": note,
        "redaction": {
            "pii_hits": redacted.pii_hits,
            "is_safe_for_model": redacted.is_safe_for_model,
        },
    }
