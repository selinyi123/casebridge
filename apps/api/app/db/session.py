import os
from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./casebridge_dev.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

BOOTSTRAP_COLUMNS: dict[str, dict[str, str]] = {
    "clients": {"organization_id": "INTEGER NOT NULL DEFAULT 1"},
    "cases": {"organization_id": "INTEGER NOT NULL DEFAULT 1"},
    "case_notes": {"organization_id": "INTEGER NOT NULL DEFAULT 1"},
    "resources": {"organization_id": "INTEGER NOT NULL DEFAULT 1"},
    "referrals": {"organization_id": "INTEGER NOT NULL DEFAULT 1"},
    "service_goals": {"organization_id": "INTEGER NOT NULL DEFAULT 1"},
    "audit_events": {"organization_id": "INTEGER NOT NULL DEFAULT 1"},
    "ai_tasks": {"organization_id": "INTEGER NOT NULL DEFAULT 1"},
    "ai_outputs": {
        "organization_id": "INTEGER NOT NULL DEFAULT 1",
        "reviewed_by": "VARCHAR(120)",
        "reviewed_at": "TIMESTAMP",
        "applied_to": "VARCHAR(120)",
    },
    "case_assessments": {"organization_id": "INTEGER NOT NULL DEFAULT 1"},
    "service_outcomes": {"organization_id": "INTEGER NOT NULL DEFAULT 1"},
}


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def ensure_bootstrap_columns() -> None:
    """Patch legacy MVP databases until Alembic owns all migrations.

    This keeps existing local/demo SQLite or Postgres volumes from breaking after
    metadata hardening. It is intentionally narrow and should be replaced by a
    first-class Alembic revision before real deployments.
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as connection:
        for table_name, columns in BOOTSTRAP_COLUMNS.items():
            if table_name not in existing_tables:
                continue
            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, ddl in columns.items():
                if column_name in existing_columns:
                    continue
                connection.execute(text(f"ALTER TABLE {_quote_identifier(table_name)} ADD COLUMN {_quote_identifier(column_name)} {ddl}"))


def init_db() -> None:
    import app.db.closure_models  # noqa: F401
    import app.db.reopen_models  # noqa: F401
    import app.db.service_plan_models  # noqa: F401
    import app.db.supervisor_review_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    ensure_bootstrap_columns()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
