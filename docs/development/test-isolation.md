# Test Isolation Strategy

## Problem

Some route-level and repository-level tests previously used the default demo database or the demo case `CASE-0001`. That made tests order-sensitive and could affect later manual demo use.

## Current implementation

Tests now use a dedicated test database fixture, an external transaction, and a data factory.

Implemented components:

- `apps/api/tests/conftest.py`
- `apps/api/tests/factories.py`
- `isolated_client`
- `test_session`
- `seed_route_case()`

The fixture creates a temporary SQLite database, initializes SQLAlchemy metadata, opens a connection-level transaction, binds a Session with `join_transaction_mode="create_savepoint"`, seeds demo users required by role-gated routes, overrides FastAPI `get_db`, and clears `app.dependency_overrides` after each test.

## Current route coverage

- Closure state route test uses `CASE-CLOSE-ROUTE` in the test database.
- Reopen state route test uses `CASE-REOPEN-ROUTE` in the test database.

## Current repository coverage

- Assessment version repository test uses `test_session`.
- Closure repository test uses `test_session`.
- Service plan repository test uses `test_session`.
- Supervisor review repository test uses `test_session`.

## Why this design

- It keeps real route dependencies active.
- It preserves JWT role checks.
- It preserves audit writes.
- It avoids touching local demo data.
- It avoids mocking repository behavior away.
- It allows code under test to call `commit()` while the outer transaction can still be rolled back.

## Future hardening

The next level is adding teardown assertions and broader migration of remaining repository tests into `test_session`.

## Non-goals

- Do not mock role boundaries away.
- Do not bypass audit writes.
- Do not hide state transitions behind fake repositories.
