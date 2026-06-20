# CaseBridge Version Roadmap

> This roadmap converts the PRD into key-node versions. Every version must advance the case-service loop, not merely add screens.

## Current baseline

- `v0.1-docs`: README, PRD, schema, AI rules, privacy design completed.
- Next target: `v0.1.1-foundation-build`.

## v0.1.1-foundation-build

Goal: make the repository buildable and demo-data ready.

Deliverables:
- seed demo cases and resources
- shared tag catalog
- Docker Compose
- FastAPI skeleton
- Next.js skeleton

Acceptance:
- repo has expected monorepo structure
- seed data covers C-0001 demo
- seed data uses only synthetic records
- AI is not called yet

## v0.1.2-business-skeleton

Goal: implement the non-AI business loop.

Deliverables:
- demo login
- clients CRUD
- cases CRUD
- case notes CRUD
- resources list
- case timeline page

Acceptance:
- user can open C-0001 profile
- user can add a visit note
- user can see notes in timeline
- user can browse resources
- no AI dependency exists

## v0.1.3-case-loop

Goal: complete the manual case loop before AI.

Deliverables:
- assessment form
- referral status flow
- service plan form
- goals and follow-up todos
- outcome tracking page

Acceptance:
- user can manually complete the 9-step demo flow
- referrals require consent before status advancement
- goals have explicit status

## v0.1.4-ai-intake-gate

Goal: add first AI capability under strict review gate.

Deliverables:
- PII redactor
- ai_tasks model
- ai_outputs model
- mocked LLM provider first
- AI intake endpoint
- output review endpoint

Acceptance:
- AI output always enters ai_outputs as pending
- apply_ai_output is the only path from AI output to formal fields
- if redaction fails, model call is blocked

## v0.1.5-resource-match-ai-reasoning

Goal: keep resource matching deterministic; use AI only for explanation.

Deliverables:
- tag-rule resource matching
- AI generated match reason draft
- referral creation only after human confirmation

Acceptance:
- candidate resources are selected by tags
- AI cannot recommend resources outside the table
- client_consent defaults to null

## v0.1.6-plan-supervision-outcome

Goal: add plan draft, supervision prompts, and outcome summary.

Deliverables:
- plan draft schema
- supervision review schema
- outcome summary schema
- risk guard rules

Acceptance:
- AI does not classify risk level
- AI does not write final conclusions
- all outputs can be accepted, modified, or rejected

## v0.2-multi-scenario

Goal: expand beyond one case type while reusing the same architecture.

Scenarios:
- elderly living alone
- family support scenario with synthetic data
- disability employment support
- new worker community support
- community conflict mediation

Acceptance:
- same model supports multiple case types
- no scenario requires one-off architecture

## v0.3-training-lab

Goal: add social-work student training mode.

Deliverables:
- virtual case library
- student assessment submission
- AI structured feedback
- teacher review
- reflection journal

Acceptance:
- training mode is separate from service mode
- student users cannot access sensitive fields

## v0.4-station-pilot

Goal: anonymous station pilot mode.

Deliverables:
- supervisor role
- resource maintenance
- export service summary
- stronger RBAC
- local deployment guide

Acceptance:
- multi-worker collaboration works for anonymized cases
- export remains redacted by default

## v1.0-institutional-version

Goal: institution-grade deployable version.

Deliverables:
- multi-tenant isolation
- complete RBAC
- formal audit dashboard
- policy/resource knowledge base
- deployment scripts
- backup and restore strategy
- report module as second-layer capability

Acceptance:
- ready for controlled private deployment only after formal compliance review
