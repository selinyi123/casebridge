# Iteration 004 Research Scan — Persistence, Timeline, and Audit Trail

> Date: 2026-06-21
> Non-repeat rule: this scan does not repeat iteration 001 (Casebook/CiviCRM/openIMIS/Flowable), iteration 002 (ODK/CommCare/KoboToolbox/OpenFn), or iteration 003 (Presidio/Guardrails/Instructor/PydanticAI). It focuses on persistence architecture, case timelines, audit trails, and social-work assessment vocabulary.

## 1. Search scope

Platforms and sources checked:

- GitHub / open-source project patterns for FastAPI + SQLAlchemy + Alembic
- public web documentation for SQLAlchemy, Alembic, and FastAPI SQL databases
- Reddit/X/Zhihu query attempts around API persistence and case-management timelines
- Chinese social-work search results around casework, direct social-work methods, and assessment vocabulary

High-signal public discussion on Reddit/X/Zhihu for this exact project category remains sparse. The useful reusable knowledge for this iteration comes mainly from official technical documentation and social-work method references.

## 2. Findings

### 2.1 SQLAlchemy 2.0 ORM

SQLAlchemy 2.0’s current ORM documentation recommends declarative mappings with `DeclarativeBase`, `Mapped`, and `mapped_column`. It distinguishes Python object models from database metadata and supports typed ORM mapping, relationships, sessions, and persistence.

Value for CaseBridge:

- The current in-memory demo store should be replaced by a database-backed model.
- CaseBridge needs explicit tables for clients, cases, notes, resources, referrals, and service goals.
- SQLAlchemy’s session model gives a clean path toward repository functions and later RBAC/audit enforcement.

Decision:

- Add SQLAlchemy models and a repository layer now.
- Keep API handlers thin: routes should call repository functions rather than own data storage logic.

Sources:

- https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- https://en.wikipedia.org/wiki/SQLAlchemy

### 2.2 Alembic migrations

Alembic is the SQLAlchemy migration tool. Its autogenerate feature compares table metadata against the current database and produces candidate migration scripts, but generated migrations still require human review.

Value for CaseBridge:

- `Base.metadata.create_all()` is acceptable only as a temporary bootstrap.
- CaseBridge must move toward explicit migration files so schema changes are traceable and reviewable.

Decision:

- Add Alembic config and a baseline migration in v0.1.3.
- Keep `create_all()` bootstrap temporarily for tests/dev until full migration workflow is enforced.

Source:

- https://alembic.sqlalchemy.org/en/latest/autogenerate.html

### 2.3 FastAPI SQL database pattern

FastAPI’s SQL database guidance uses dependency-injected sessions and explicit table models. This aligns with CaseBridge’s need to keep route functions small and testable.

Value for CaseBridge:

- Use `get_db()` dependency for request-scoped sessions.
- Keep seed/bootstrap code separate from API handlers.
- Tests should run inside FastAPI lifespan context so startup initialization works.

Source:

- https://fastapi.tiangolo.com/tutorial/sql-databases/

### 2.4 Social-work method vocabulary

Public social-work references describe direct social-work methods across micro, mezzo, and macro levels, including individual/family casework, group work, and community work. Casework emphasizes one-to-one professional helping relationships and the interaction between the person and social environment.

Value for CaseBridge:

- The database model should not only store a “client record”; it needs a service timeline.
- Future assessment forms should encode person-in-environment, strengths, family/community support, service goals, and follow-up status.
- The MVP remains casework-first, but later versions should support group and community work without rewriting the core.

Sources:

- https://zh.wikipedia.org/wiki/社会工作
- https://zh.wikipedia.org/wiki/个案工作

## 3. Applied decisions in this iteration

Implemented:

- SQLAlchemy declarative base
- persistent models for clients, cases, notes, resources, referrals, and service goals
- database session and startup seed loader
- repository layer
- routers switched from in-memory store to persistent repository
- Alembic config and baseline migration
- tests updated to run inside lifespan context

## 4. Design implications for next node

Next version should focus on front-end visibility and manual workflow:

- C-0001 profile page
- case timeline UI
- note creation form
- resource matching panel
- manual service-goal creation
- referral state transition rules

Do not add real AI yet. AI integration begins only after the persistent manual loop is visible and testable.

## 5. Non-repeat rule for next research

Next iteration must not repeat SQLAlchemy/Alembic/FastAPI basics. Suggested next focus:

1. UI patterns for case timeline and resource matching
2. design systems for internal tools and social-service dashboards
3. China-localized assessment form dimensions for elderly/community service
4. consent-state and referral-state modeling in sensitive service systems
