# Test Isolation Strategy

## Current problem

Some route-level tests previously mutated the demo case `CASE-0001`. That made tests order-sensitive and could affect later manual demo use.

## Current mitigation

Route tests now seed dedicated test cases through `apps/api/tests/factories.py`.

- Closure state route test uses `CASE-CLOSE-ROUTE`.
- Reopen state route test uses `CASE-REOPEN-ROUTE`.
- Shared helper: `seed_route_case()`.

This reduces direct demo-case pollution while keeping the existing app and database wiring unchanged.

## Future hardening

The next level is a dedicated test database fixture:

1. Use a temporary SQLite file per test session.
2. Override FastAPI `get_db` with `app.dependency_overrides`.
3. Create schema once for the test database.
4. Seed only the data each route contract needs.
5. Reset overrides after each test module.

## Non-goals

- Do not mock role boundaries away.
- Do not bypass audit writes.
- Do not hide state transitions behind fake repositories.
