# Iteration 006 Research Scan — Manual Service Goals, Resource Links, and Agreement Gate

> Date: 2026-06-21
> Non-repeat rule: this scan does not repeat iteration 001-005. It focuses on service goals, resource/referral lifecycle, agreement-state gates, and human-service information-and-referral patterns.

## 1. Search scope

Platforms and sources checked:

- GitHub/open-source search for human-service referral and case-management components
- public web references around 211 information-and-referral systems
- public references around Open Referral / human services resource directories
- public references around service plan / goal-oriented casework concepts
- Reddit/X/Zhihu query attempts around referral workflow, consent state, and social-work case goals

High-signal Reddit/X/Zhihu results for the exact CaseBridge niche remained sparse. Useful reusable ideas came mainly from information-and-referral standards, human-service directory models, and casework theory.

## 2. Findings

### 2.1 Information-and-referral systems separate resource discovery from action

211-style information-and-referral systems exist to connect people to health, human, and social service organizations. They depend on maintained resource directories and standard taxonomies. The key design lesson is that finding a candidate resource is not the same as completing a referral or proving service delivery.

Value for CaseBridge:

- Resource matching should remain a candidate-generation step.
- A referral/link object must be manually created and tracked.
- Status transitions must be auditable and should require explicit agreement state for higher-commitment statuses.

Decision:

- Add manual resource-link creation from matched candidates.
- Keep candidate matching deterministic.
- Block high-commitment status transitions without agreement state.

Sources:

- https://en.wikipedia.org/wiki/211_(telephone_number)
- https://www.211.org/

### 2.2 Open Referral / human-service data direction

Open Referral and related human-service data efforts emphasize structured service, organization, location, and contact data. This supports the CaseBridge decision to keep resources as separate records with stable codes and tags, not hallucinated text.

Value for CaseBridge:

- Resources should be existing database rows.
- Matching should return resource codes, not free-form suggestions.
- Later versions may need richer service taxonomy, eligibility, location, and contact fields.

Decision:

- Keep `resources` table as source of truth.
- Add manual resource link/referral object that references `resource_code`.
- Do not allow AI or UI to create a referral to a non-existing resource.

### 2.3 Service goals are separate from notes

In casework, notes document interactions; goals describe intended changes and planned direction. Mixing them makes it hard to measure progress.

Value for CaseBridge:

- `case_notes` should remain interaction records.
- `service_goals` should become first-class objects.
- Timeline can later merge notes/goals/referrals, but storage should keep them separate.

Decision:

- Add service-goal API and UI now.
- Keep goal creation manual before AI-generated plans exist.

### 2.4 Agreement-state gate

For sensitive service systems, a resource link should not silently advance from candidate/verification to active referral/result without some explicit agreement/consent marker. In CaseBridge MVP, this is named `agreement_status` rather than a legally complete consent record.

Value for CaseBridge:

- The UI and API should encode that a matched resource is not automatically authorized.
- The API should reject status transitions to `referred`, `success`, or `completed` when `agreement_status` is still `none` or `expired`.

Decision:

- Add `agreement_status` gate for resource link status transitions.
- Tests must verify blocked and allowed transitions.

## 3. Applied decisions in this iteration

Implemented:

- service-goal request schema
- resource-link/referral request schema
- repository functions for service goals and resource links
- agreement-state guard for status transitions
- service-goal routes
- referral/resource-link routes
- C-0001 workspace UI for manual goals and links
- tests for service goal creation and agreement gate

## 4. Next design implications

Next version should improve timeline and review visibility:

- unified timeline event shape
- display notes + goals + resource links together
- resource link status UI with blocked transition feedback
- clear labels for agreement-state vs production consent

Do not add AI until manual goal/link/review workflows are usable.

## 5. Non-repeat rule for next research

Next iteration must not repeat service goal/resource-link basics. Suggested next focus:

1. unified timeline/event-sourcing-lite patterns
2. audit log schema and UI for sensitive service records
3. social-work outcome tracking dimensions
4. AI intake review UX after manual loop completion
