from app.db.models import CaseRecord, Client
from app.db.session import SessionLocal


def seed_route_case(case_id: str, *, status: str = "open", stage: str = "intake") -> None:
    with SessionLocal() as db:
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
