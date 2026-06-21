from fastapi import APIRouter

from app.core.demo_store import TAG_CATALOG, list_resources
from app.core.resource_match import match_resources

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("")
def index() -> dict:
    return {"items": list_resources()}


@router.post("/match")
def match(payload: dict) -> dict:
    need_tag_codes = payload.get("need_tag_codes") or []
    return {"candidates": match_resources(need_tag_codes, list_resources(), TAG_CATALOG)}
