from fastapi import APIRouter

from app.core.demo_store import TAG_CATALOG, list_resources
from app.core.resource_match import match_resources
from app.schemas import ResourceMatchRequest

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("")
def index() -> dict:
    return {"items": list_resources()}


@router.post("/match")
def match(payload: ResourceMatchRequest) -> dict:
    return {"candidates": match_resources(payload.need_tag_codes, list_resources(), TAG_CATALOG)}
