# CaseBridge Security Notes

## Current MVP security posture

CaseBridge v0.1.x is still a demo/MVP codebase. The following controls are now enforced in code, but this is not yet a real-data-ready deployment.

## Implemented controls

### Auth / RBAC

- Write actions require JWT authentication.
- `social_worker` and `admin` can perform case write operations.
- Raw case-note access is admin-only.
- AI review/apply actions use the authenticated user as reviewer, not a client-provided reviewer identity.

### AI review gate

- AI output remains draft-only in `ai_outputs`.
- AI output requires human review before apply.
- Apply requires explicit responsibility acceptance.
- Applied AI outputs are marked via `applied_to` and cannot be applied repeatedly.

### Privacy / PII

- Raw case-note content is hidden by default.
- Default note display uses `content_clean` / `content_display`.
- Rule-based redaction masks common structured PII.
- Minor and health/diagnosis clues block model-safety status for AI processing.

### Organization scoping

- Repository readers and writers support `organization_id` filtering.
- Writer functions defensively verify that target case/resource/note records belong to the same organization before mutation.
- Route-level write operations pass the authenticated user's organization into repository calls.
- Cross-organization case IDs are rejected at the repository layer, not only the router layer.

## Known remaining gaps

These are intentionally not solved in this MVP patch:

1. Replace bootstrap column backfill with first-class Alembic migrations.
2. Enforce organization scope on every future repository function by default through a shared query abstraction.
3. Replace rule-based redaction with a production DLP/de-identification service before any real data use.
4. Add permission tests for every route-level raw-data and export path.
5. Rotate demo credentials and require environment-provided secrets outside local development.
