from fastapi import APIRouter, HTTPException

from app.core.demo_store import get_client, list_cases, list_clients

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("")
def index() -> dict:
    return {"items": list_clients()}


@router.get("/{client_code}")
def show(client_code: str) -> dict:
    client = get_client(client_code)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    return {"client": client, "cases": list_cases(client_code=client_code)}
