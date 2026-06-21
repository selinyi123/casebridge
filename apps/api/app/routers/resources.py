from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.demo_store import TAG_CATALOG
from app.core.resource_match import match_resources
from app.db.persistent_repository import list_resources
from app.db.session import get_db
from app.schemas import ResourceMatchRequest

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("")
def index(db: Session = Depends(get_db)) -> dict:
    return {"items": list_resources(db)}


@router.post("/match")
def match(payload: ResourceMatchRequest, db: Session = Depends(get_db)) -> dict:
    return {"candidates": match_resources(payload.need_tag_codes, list_resources(db), TAG_CATALOG)}
