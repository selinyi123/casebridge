# Iteration 001 Research Scan — CaseBridge

> Date: 2026-06-20
> Scope: public references for AI-native case management, social service workflows, open-source components, and hackathon-style delivery.
> Rule: each research iteration should avoid repeating the same focus. This first scan focuses on architecture references and reusable components, not feature brainstorming.

## 1. Findings

### 1.1 Casebook: human services case-management baseline

Casebook is a human services SaaS platform that grew from child-welfare case-management work and later expanded to broader human-services organizations.

Reference value for CaseBridge:
- intake → case management → assessment → reporting workflow
- human-services data model
- multi-program service context

Do not copy directly:
- US child-welfare / nonprofit service model is not the same as Chinese social work station practice.
- CaseBridge needs local resource collaboration, social-work theory, consent, privacy, and AI review gates.

Source:
- https://www.casebook.net/
- https://en.wikipedia.org/wiki/Casebook_PBC

### 1.2 CiviCRM / CiviCase: nonprofit CRM and continuous interaction tracking

CiviCRM is an open-source CRM for nonprofits and advocacy organizations. CiviCase tracks complex interactions, tasks, and follow-up activities between an organization and a service contact.

Reference value for CaseBridge:
- contact / relationship / activity / permission model
- case as a set of continuous interactions rather than a single record
- extensible nonprofit CRM architecture

Do not copy directly:
- CiviCRM is broad CRM; CaseBridge must remain social-work case-service centric.
- PHP/CMS stack does not match the current Next.js + FastAPI plan.

Sources:
- https://civicrm.org/
- https://docs.civicrm.org/user/en/latest/case-management/what-is-civicase/
- https://en.wikipedia.org/wiki/CiviCRM

### 1.3 openIMIS / OpenSPP direction: beneficiary and social-protection system reference

openIMIS is an open-source platform for health financing and social-protection schemes; it links beneficiary, provider, and payer data and is recognized as a Digital Public Good.

Reference value for CaseBridge:
- beneficiary / service provider / entitlement / programme concepts
- social-protection data governance
- AGPL-style public-good software positioning

Do not copy directly:
- openIMIS is scheme administration, not social-work casework.
- CaseBridge should not become benefit adjudication or eligibility-decision software.

Source:
- https://openimis.org/
- https://en.wikipedia.org/wiki/OpenIMIS

### 1.4 Flowable / CMMN: workflow and case-management notation reference

Flowable is an open-source workflow and case-management engine supporting BPMN, CMMN, and DMN.

Reference value for CaseBridge:
- state machines
- process history
- auditable case progression
- case/task lifecycle thinking

Decision for MVP:
- Do not add Flowable or a full CMMN engine now.
- Implement lightweight explicit status fields and state machines in PostgreSQL/FastAPI first.
- Revisit workflow engines only after V0.4 when multiple case types, roles, and institutions create real orchestration complexity.

Sources:
- https://github.com/flowable/flowable-engine
- https://en.wikipedia.org/wiki/Flowable
- https://arxiv.org/abs/1608.05011

### 1.5 AI for social service: opportunity and risk

Recent research on GenAI in social service shows opportunities in documentation, assessment, and supervision support, but also risks: overreliance, algorithmic bias, professional identity weakening, and client-safety concerns.

Reference value for CaseBridge:
- AI should assist documentation, assessment support, and supervision prompts.
- AI must not automate judgments, eligibility, risk classification, or intervention decisions.
- Human review and auditability are not optional.

Sources:
- https://arxiv.org/abs/2502.19822
- https://arxiv.org/abs/2303.09743
- https://arxiv.org/abs/2204.02310

### 1.6 Hackathon delivery pattern

Public-interest hackathons such as Random Hacks of Kindness emphasize open-source outputs for real-world charity/nonprofit problems. GovHack shows open-data projects can be turned into public-service prototypes.

Reference value for CaseBridge:
- Build a demonstrable narrow prototype, not a broad concept deck.
- Use open-source components and public, synthetic, or anonymized datasets.
- Prioritize usefulness and novelty through a clear service workflow.

Sources:
- https://en.wikipedia.org/wiki/Random_Hacks_of_Kindness
- https://en.wikipedia.org/wiki/GovHack
- https://arxiv.org/abs/2503.04290

## 2. Component decisions for the current build

| Area | Decision | Reason |
| --- | --- | --- |
| Case workflow | Lightweight state machine in app code | MVP is single-case closed loop; full BPM/CMMN is overkill |
| CRM model | Borrow contact/activity concepts, not the stack | CiviCRM is useful conceptually, but too broad |
| Social protection | Borrow beneficiary/provider/programme thinking | Do not become eligibility engine |
| AI | Keep AI as draft + review gate | High-sensitivity domain requires human responsibility |
| Resource matching | Start with tag rules | Faster, auditable, easier to explain in demo |
| Privacy | PII redaction before model calls | Required for social-service data safety |
| Seed data | Synthetic only | Avoid real PII and legal/ethical risk |

## 3. Resulting design change for v0.1.1

Add a version node called `v0.1.1-foundation-build`:

- seed demo cases and resources
- initialize code skeleton
- add shared tag catalog
- add Docker Compose for API / web / PostgreSQL / Redis / MinIO
- keep AI integration mocked until Phase 2

## 4. Non-repeat rule for next research

Next research iteration should not repeat Casebook/CiviCRM/openIMIS/Flowable basics. Suggested next focus:

1. Chinese social-work station systems and government procurement clues
2. domestic AI policy-assistant / community-governance products
3. practical UI patterns for case timeline + resource matching
4. privacy-preserving LLM implementation patterns for sensitive records
