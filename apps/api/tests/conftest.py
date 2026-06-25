from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.db.closure_models  # noqa: F401
import app.db.reopen_models  # noqa: F401
import app.db.service_plan_models  # noqa: F401
import app.db.supervisor_review_models  # noqa: F401
from app.core.auth import hash_password
from app.db.base import Base
from app.db.models import User
from app.db.session import get_db
from app.main import app


@pytest.fixture()
def test_session(tmp_path) -> Generator[Session, None, None]:
    database_path = tmp_path / "casebridge_test.db"
    engine = create_engine(f"sqlite:///{database_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False, expire_on_commit=False, join_transaction_mode="create_savepoint")
    session = TestingSessionLocal()
    session.add_all(
        [
            User(username="demo_social_worker", email="worker@example.invalid", password_hash=hash_password("test-only"), display_name="Demo Social Worker", role="social_worker", organization_id=1),
            User(username="demo_supervisor", email="supervisor@example.invalid", password_hash=hash_password("test-only"), display_name="Demo Supervisor", role="supervisor", organization_id=1),
            User(username="demo_admin", email="admin@example.invalid", password_hash=hash_password("test-only"), display_name="Demo Admin", role="admin", organization_id=1),
        ]
    )
    session.commit()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


@pytest.fixture()
def isolated_client(test_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        app.dependency_overrides = {}
