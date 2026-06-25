# Test Isolation Strategy

## Problem

Some route-level tests previously mutated the demo case `CASE-0001`. That made tests order-sensitive and could affect later manual demo use.

## Current implementation

Route tests now use a dedicated test database fixture and route data factory.

Implemented components:

- `apps/api/tests/conftest.py`
- `apps/api/tests/factories.py`
- `isolated_client`
- `test_session`
- `seed_route_case()`

The fixture creates a temporary SQLite database, initializes SQLAlchemy metadata, seeds demo users required by role-gated routes, overrides FastAPI `get_db`, and clears `app.dependency_overrides` after each test.

## Current route coverage

- Closure state route test uses `CASE-CLOSE-ROUTE` in the test database.
- Reopen state route test uses `CASE-REOPEN-ROUTE` in the test database.

## Why this design

- It keeps real route dependencies active.
- It preserves JWT role checks.
- It preserves audit writes.
- It avoids touching local demo data.

## Future hardening

The next level is transaction rollback per test or a dedicated test database per module with stricter teardown checks.

## Non-goals

- Do not mock role boundaries away.
- Do not bypass audit writes.
- Do not hide state transitions behind fake repositories.
