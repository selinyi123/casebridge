# Iteration 005 Research Scan — Case UI, Resource Matching Panel, and Service Loop Visibility

> Date: 2026-06-21
> Non-repeat rule: this scan does not repeat iteration 001 (case-management baselines), iteration 002 (field-data/offline tools), iteration 003 (privacy/guardrails), or iteration 004 (SQLAlchemy/Alembic/FastAPI persistence). It focuses on user-interface patterns for case timelines, resource matching, and service-loop visibility.

## 1. Search scope

Platforms and sources checked:

- GitHub/open-source references for React dashboards, timeline/activity feeds, and internal tools
- public web references for React/Next.js UI implementation patterns
- public references for social casework timeline and psychosocial assessment concepts
- Reddit/X/Zhihu query attempts around case timeline UI and case-management dashboards

Public Reddit/X/Zhihu results remained low-signal for the exact CaseBridge niche. The useful references are general internal-tool UI patterns and social-work casework concepts.

## 2. Findings

### 2.1 React/Next.js component-first UI

React is a component-based UI library. In CaseBridge, this suggests the UI should be decomposed into stable panels rather than one large page: profile card, case status, timeline, note form, resource list, and matching panel.

Value for CaseBridge:

- Build a clear case workspace instead of a generic dashboard.
- Keep UI state local for v0.1.3; do not introduce global state libraries yet.
- Use browser-side fetch for manual demo actions such as creating notes and triggering resource matching.

Decision:

- Implement a minimal `/clients/c-0001` case workspace page.
- Use simple TypeScript and browser fetch.
- Avoid adding design-system dependencies until the workflow is proven.

Source:

- https://react.dev/
- https://nextjs.org/docs

### 2.2 Timeline/activity-feed pattern

Casework is a sequence of interactions, not a single form. A service timeline should display visit notes and later referrals/goals/outcomes as chronological records.

Value for CaseBridge:

- C-0001 needs an obvious service history view.
- The timeline should preserve raw notes and distinguish human input from AI draft output later.
- Timeline is the main proof that CaseBridge is a continuous support system, not a one-shot assessment tool.

Decision:

- Build timeline first using `case_notes`.
- Later extend timeline with referrals, service goals, review items, and outcome updates.

### 2.3 Resource matching panel pattern

The resource matching panel should show candidate resources, match reasons, and human-verification requirements. It must not look like an automatic decision engine.

Value for CaseBridge:

- Good UI copy matters: use “candidate resources” and “requires human verification”.
- Candidate selection must remain deterministic in v0.1.3.
- AI explanation can be added later, but not before manual review gate exists.

Decision:

- Add a resource matching panel that takes current need tags from C-0001.
- Display matched codes and verification requirement.
- Do not create referrals automatically from matching results.

### 2.4 Social-work casework framing

Social casework focuses on a professional helping relationship and a person-in-environment understanding. Public references describe psychosocial assessment as a key tool and emphasize helping the person face problems within their strengths and environment rather than “solving for” the client.

Value for CaseBridge:

- UI labels must not reduce the client to a “ticket”.
- Use language such as concern, support, note, resource candidate, follow-up, and review.
- Future assessment UI should encode strengths, environment, client intention, and support network.

Source:

- https://en.wikipedia.org/wiki/Caseworker
- https://zh.wikipedia.org/wiki/个案工作

## 3. Applied decisions in this iteration

Implemented or planned for this node:

- C-0001 workspace page
- profile card
- case summary card
- visit-note timeline
- note creation form
- resource list
- deterministic resource matching panel
- homepage link to the case workspace

## 4. Design implications for next node

After the workspace is visible, the next practical extension should be:

- service-goal endpoint and UI
- referral endpoint and UI
- consent/agreement gate for referral status transitions
- timeline union view combining notes, referrals, and goals

Do not add real AI until those manual workflow elements are visible and testable.

## 5. Non-repeat rule for next research

Next iteration should not repeat UI component basics. Suggested next focus:

1. referral consent/agreement-state modeling
2. service-goal and outcome-tracking data model
3. elder-care service assessment dimensions in Chinese social-work practice
4. internal audit trail UI and event-sourcing-lite patterns
