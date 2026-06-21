from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.persistent_repository import get_client, list_cases, list_clients
from app.db.session import get_db

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("")
def index(db: Session = Depends(get_db)) -> dict:
    return {"items": list_clients(db)}


@router.get("/{client_code}")
def show(client_code: str, db: Session = Depends(get_db)) -> dict:
    client = get_client(db, client_code)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    return {"client": client, "cases": list_cases(db, client_code=client_code)}
