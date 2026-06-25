from sqlalchemy.orm import Session

from app.db.models import CaseRecord, Client
from app.db.session import SessionLocal


def _seed_route_case(db: Session, case_id: str, *, status: str = "open", stage: str = "intake") -> None:
    db.merge(
        Client(
            code="CLIENT-ROUTE-TEST",
            organization_id=1,
            display_name="Route Test Client",
            age=80,
            community="Test",
            client_type="demo",
            primary_concern="Route test",
        )
    )
    db.merge(
        CaseRecord(
            id=case_id,
            organization_id=1,
            client_code="CLIENT-ROUTE-TEST",
            title="Route test case",
            stage=stage,
            status=status,
        )
    )
    db.commit()


def seed_route_case(case_id: str, *, status: str = "open", stage: str = "intake", db: Session | None = None) -> None:
    if db is not None:
        _seed_route_case(db, case_id, status=status, stage=stage)
        return
    with SessionLocal() as session:
        _seed_route_case(session, case_id, status=status, stage=stage)
