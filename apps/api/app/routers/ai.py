from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.prompt_registry import get_prompt_spec
from app.ai.provider_registry import generate_with_provider
from app.ai.redaction_gateway import run_redaction_gate
from app.db.persistent_repository import (
    apply_ai_output_to_assessment,
    create_ai_intake_output,
    create_apply_preview,
    get_case,
    get_note,
    list_ai_outputs,
    review_ai_output,
)
from app.db.session import get_db
from app.schemas import ApplyAiOutputRequest, GenerateAiIntakeRequest, ReviewAiOutputRequest

router = APIRouter(prefix="/cases/{case_id}/ai", tags=["ai"])
DEFAULT_PROMPT_VERSION = "intake-v0.1.7"
DEFAULT_PROVIDER = "mock"


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
    redaction = run_redaction_gate(note.get("content_raw", ""))
    if redaction.report.blocked:
        raise HTTPException(status_code=409, detail={"error": "redaction_gate_blocked", "report": redaction.report.__dict__})
    prompt = get_prompt_spec(DEFAULT_PROMPT_VERSION)
    provider_result = generate_with_provider(DEFAULT_PROVIDER, prompt, redaction.clean_text)
    output = create_ai_intake_output(
        db,
        case_id=case_id,
        note_id=payload.note_id,
        parsed_output=provider_result.output.model_dump(),
        provider=provider_result.provider,
        prompt_version=provider_result.prompt_version,
    )
    return {
        "output": output,
        "redaction": redaction.report.__dict__,
        "provider": provider_result.provider,
        "prompt_version": provider_result.prompt_version,
    }


@router.patch("/outputs/{output_id}/review")
def review(case_id: str, output_id: str, payload: ReviewAiOutputRequest, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        output = review_ai_output(
            db=db,
            case_id=case_id,
            output_id=output_id,
            review_status=payload.review_status,
            reviewer_id=payload.reviewer_id,
            reviewer_notes=payload.reviewer_notes,
            modified_output=payload.modified_output,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not output:
        raise HTTPException(status_code=404, detail="ai_output_not_found")
    return {"output": output}


@router.post("/outputs/{output_id}/apply-preview")
def apply_preview(case_id: str, output_id: str, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        preview = create_apply_preview(db, case_id, output_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not preview:
        raise HTTPException(status_code=404, detail="ai_output_not_found")
    return {"preview": preview}


@router.post("/outputs/{output_id}/apply-to-assessment")
def apply_to_assessment(case_id: str, output_id: str, payload: ApplyAiOutputRequest, db: Session = Depends(get_db)) -> dict:
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="case_not_found")
    try:
        assessment = apply_ai_output_to_assessment(
            db,
            case_id=case_id,
            output_id=output_id,
            reviewer_id=payload.reviewer_id,
            responsibility_accepted=payload.reviewer_responsibility_accepted,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not assessment:
        raise HTTPException(status_code=404, detail="ai_output_not_found")
    return {"assessment": assessment}
