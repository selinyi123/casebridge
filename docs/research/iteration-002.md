# Iteration 002 Research Scan — Field Data, Forms, and Offline Case Records

> Date: 2026-06-21
> Non-repeat rule: this scan does not repeat the Casebook / CiviCRM / openIMIS / Flowable baseline from iteration 001. It focuses on field data collection, form engines, offline-first service records, and practical components for CaseBridge v0.1.2-v0.1.4.

## 1. Search scope

Platforms and sources checked:

- GitHub and open-source project pages
- hackathon / civic-tech delivery patterns
- Reddit / X / Chinese-platform query attempts
- public web search for Chinese social-work station systems
- research references around social-service AI and field data systems

Note: direct public search for Reddit/X/Zhihu/Xiaohongshu/Weibo produced sparse or low-signal results for this exact project category. No reliable public same-position Chinese AI-native social-work Casebook was confirmed in this iteration.

## 2. Findings

### 2.1 ODK: offline-first field data collection

ODK is an open-source data collection platform for mobile and web forms. It supports online/offline collection, updates to persistent records called Entities, REST API integration, audit logs, role-based access control, encryption, and map/geospatial features.

Value for CaseBridge:

- Offline/field-visit design matters for social-work visits.
- Structured forms should support validation, branching, and repeat sections.
- Persistent person/place records are important; ODK Entities confirm the need for long-lived client/resource records.
- Audit logs and RBAC are not optional in sensitive field data systems.

Decision:

- Do not embed ODK in v0.1.x.
- Borrow ODK-style form discipline: validation, repeatable notes, audit, and future offline sync.
- Revisit integration only after CaseBridge has real mobile/offline needs.

Sources:

- https://getodk.org/
- https://github.com/getodk
- https://docs.getodk.org/entities-intro/
- https://en.wikipedia.org/wiki/ODK_(software)

### 2.2 CommCare: mobile client management and decision support

CommCare is an open-source mobile platform used in low-resource settings for data collection, client management, decision support, visits, multimedia prompts, offline mobile work, and scheduled reminders.

Value for CaseBridge:

- Client-facing worker workflows are usually visit-centered, not dashboard-centered.
- Decision support must be structured and constrained, not free-form AI autonomy.
- Offline visit data and reminders are important later.

Decision:

- Do not clone CommCare.
- Borrow its pattern: visit workflow + client record + guided decision support + reminders.
- CaseBridge should keep AI as reviewable assistance, not automated decision support.

Sources:

- https://www.dimagi.com/commcare/
- https://github.com/dimagi/commcare-hq
- https://en.wikipedia.org/wiki/Dimagi

### 2.3 KoboToolbox: humanitarian form builder and response management

KoboToolbox is an open-source data collection platform used by humanitarian and development organizations. It uses ODK/XLSForm-style forms, web-based builders, mobile/web collection, and APIs.

Value for CaseBridge:

- CaseBridge may later need a configurable assessment form builder.
- Current MVP should not build a full form builder.
- A static assessment schema is enough for v0.1.x.

Decision:

- Do not build a full visual form builder now.
- Add `assessment_templates` later only if repeated case-type forms become necessary.

Sources:

- https://www.kobotoolbox.org/
- https://github.com/kobotoolbox/kpi

### 2.4 OpenFn: workflow integration for public-benefit data systems

OpenFn is an open-source integration platform often used in global health and public-benefit contexts to move data between systems through jobs and adapters.

Value for CaseBridge:

- Later station pilots may need integrations with spreadsheets, forms, messaging, and reporting systems.
- v0.1.x should not start with integration complexity.

Decision:

- Keep a clean API boundary.
- Add export/import jobs after business loop stabilizes.

Sources:

- https://www.openfn.org/
- https://github.com/OpenFn/lightning

### 2.5 Chinese platform search result

Queries around “社工站 信息化 个案管理 系统”, “智慧社工平台”, and “AI 社工 个案管理” returned scattered material, but no clearly open-source, AI-native, China-localized CaseBridge equivalent was confirmed.

Interpretation:

- There may be government-procurement or vendor-built systems that are not openly indexed.
- CaseBridge should avoid claiming “no one has done this”.
- Safer positioning: existing systems are likely fragmented across community governance, civil-affairs information systems, form/statistics tools, and internal vendor platforms; CaseBridge’s difference is AI-native case-service loop + social-work theory + review gate + resource collaboration.

## 3. Component decisions for v0.1.2

| Area | Decision | Reason |
| --- | --- | --- |
| Forms | Use fixed schemas now | Full form builder is premature |
| Offline | Defer offline sync | Web MVP first, but model should support visit notes |
| Client record | Keep persistent client/case/time-line model | ODK/CommCare confirm long-lived records matter |
| Decision support | Constrained suggestions only | Avoid AI or rule engine making final decisions |
| Resource matching | Deterministic tag rules | Auditable and easy to demo |
| Integration | API boundary only | OpenFn-style integrations are later work |
| Mobile | Web responsive later | Do not build app or mini-program in MVP |

## 4. Design implications

Add to v0.1.2:

- explicit visit-note APIs
- deterministic resource matching endpoint
- C-0001 profile and timeline endpoint
- no database dependency yet if time is limited; but API shape must match future DB model
- clean separation between demo data and future persistent storage

Add to v0.1.3:

- real database models
- assessment form
- referral status transitions
- service goal tracking

Add to v0.1.4:

- AI intake under review gate
- PII redaction before any provider call
- ai_tasks / ai_outputs persistence

## 5. Non-repeat rule for next research

Next iteration must not repeat ODK/CommCare/KoboToolbox/OpenFn basics. Suggested next focus:

1. social-work assessment frameworks and validated assessment form structures
2. privacy-preserving LLM redaction patterns and DLP libraries
3. UI patterns for case timeline and resource matching
4. China community-service and civil-affairs data vocabulary
