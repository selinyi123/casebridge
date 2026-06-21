from fastapi import APIRouter, HTTPException

from app.assessment_catalog import get_schema

router = APIRouter(prefix="/assessment-schemas", tags=["assessment-schemas"])


@router.get("/{schema_id}")
def show(schema_id: str) -> dict:
    try:
        return {"schema": get_schema(schema_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
