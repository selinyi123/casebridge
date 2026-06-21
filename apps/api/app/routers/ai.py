from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.mock_provider import generate_intake_draft
from app.core.privacy import redact_text
from app.db.persistent_repository import create_ai_intake_output, get_case, get_note, list_ai_outputs, review_ai_output
from app.db.session import get_db
from app.schemas import GenerateAiIntakeRequest, ReviewAiOutputRequest

router = APIRouter(prefix="/cases/{case_id}/ai", tags=["ai"])


@router.get("/outputs")
def outputs(case_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    return {"items": list_ai_outputs(db, case_id)}


@router.post("/intake")
def generate_intake(case_id: str, payload: GenerateAiIntakeRequest, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    note = get_note(db, payload.note_id)
    if not note or note.get("case_id") != case_id:
        raise HTTPException(status_code=404, detail="note_not_found")
    redacted = redact_text(note.get("content_raw", ""))
    draft = generate_intake_draft(redacted.clean_text)
    output = create_ai_intake_output(db, case_id=case_id, note_id=payload.note_id, parsed_output=draft.model_dump())
    return {"output": output, "redaction": {"pii_hits": redacted.pii_hits, "is_safe_for_model": redacted.is_safe_for_model}}


@router.patch("/outputs/{output_id}/review")
def review(case_id: str, output_id: str, payload: ReviewAiOutputRequest, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    output = review_ai_output(
        db=db,
        output_id=output_id,
        review_status=payload.review_status,
        reviewer_notes=payload.reviewer_notes,
        modified_output=payload.modified_output,
    )
    if not output or output.get("case_id") != case_id:
        raise HTTPException(status_code=404, detail="ai_output_not_found")
    return {"output": output}
