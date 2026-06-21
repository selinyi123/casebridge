# Iteration 003 Research Scan — Privacy Redaction and LLM Guardrails

> Date: 2026-06-21
> Non-repeat rule: this scan does not repeat iteration 001 (Casebook/CiviCRM/openIMIS/Flowable) or iteration 002 (ODK/CommCare/KoboToolbox/OpenFn). It focuses on sensitive-data redaction, structured output validation, and guardrail components for CaseBridge v0.1.4+.

## 1. Search scope

Platforms and sources checked:

- GitHub open-source privacy and LLM guardrail repositories
- public web search for PII redaction and LLM structured output libraries
- Reddit/X/Zhihu query attempts for social-work AI privacy patterns
- recent research on LLM structured-output failures and tool-use guardrails

Public discussion on Reddit/X/Zhihu around the exact combination of “AI social-work case management + PII redaction + China-localized workflow” remained low-signal. The useful reusable components are mostly general privacy/LLM infrastructure rather than social-work-specific projects.

## 2. Findings

### 2.1 Microsoft Presidio

Presidio is an open-source framework for detecting, redacting, masking, and anonymizing sensitive data across text, images, and structured data. It supports NLP, pattern matching, customizable recognizers, Python/Docker/Kubernetes usage, and text/image de-identification.

Value for CaseBridge:

- Strong candidate for the future `PII Redactor` service.
- Custom recognizers are important for China-specific sensitive terms and social-work records.
- Presidio’s own docs warn that automated detection is not guaranteed to catch all sensitive information, so CaseBridge must keep human review and additional safeguards.

Decision:

- Do not add Presidio dependency to v0.1.2.
- Add a stronger local MVP redactor now.
- Plan Presidio-style service for v0.1.4 or v0.4 pilot readiness.

Source:

- https://github.com/microsoft/presidio

### 2.2 Guardrails AI / NeMo Guardrails direction

Guardrail libraries provide runtime constraints, validators, and structured-output enforcement for LLM applications.

Value for CaseBridge:

- AI outputs must validate against schema before becoming reviewable drafts.
- Guardrails are not a substitute for human review; they are a pre-review filter.
- Runtime rails should reject outputs that contain final judgments, unsafe certainty, or non-existing resource IDs.

Decision:

- Do not adopt a large guardrail framework before the first AI endpoint.
- Implement lightweight `Risk Guard` and Pydantic schema validation first.
- Revisit Guardrails/NeMo after v0.1.4 if custom validators become hard to maintain.

Sources:

- https://github.com/guardrails-ai/guardrails
- https://arxiv.org/abs/2310.10501

### 2.3 Structured output libraries: Instructor / PydanticAI

Instructor and PydanticAI show a common direction: use typed Python models and schema validation for LLM structured outputs.

Value for CaseBridge:

- AI output should be parsed into typed schemas, not free text.
- Any invalid output should fail closed and remain unapplied.
- API request payloads should also use typed schemas now to reduce bug surface.

Decision:

- Add Pydantic request schemas immediately for current non-AI endpoints.
- For AI endpoints, use explicit Pydantic output schemas before model calls are added.

Sources:

- https://github.com/567-labs/instructor
- https://github.com/pydantic/pydantic-ai

### 2.4 Recent structured-output and tool-use safety research

Recent research emphasizes that structured outputs can still fail through truncation, malformed JSON, field-level errors, and mid-trajectory leaks in tool-using systems.

Value for CaseBridge:

- JSON mode alone is insufficient.
- Need schema validation, retry/fail-closed behavior, and review gate.
- In future agentic workflow, intermediate traces must be audited, not just final answers.

Sources:

- https://arxiv.org/abs/2605.13076
- https://arxiv.org/abs/2603.18014
- https://arxiv.org/abs/2604.07223

## 3. Immediate fixes for current code

Applied in this iteration:

- strengthened MVP privacy redactor without adding external dependency
- added Pydantic request schemas for case note creation and resource matching
- added validation tests for bad payloads and redaction behavior
- added CORS baseline for local web app usage

## 4. Component decisions for next versions

| Version | Decision |
| --- | --- |
| v0.1.2 | Keep local MVP redactor and typed request schemas |
| v0.1.3 | Add persistence, not real AI |
| v0.1.4 | Add typed AI output schemas + review gate |
| v0.1.5 | Add deterministic resource matching plus AI explanation only |
| v0.4 | Evaluate Presidio-style production redactor and custom recognizers |

## 5. Non-repeat rule for next research

Next research must not repeat Presidio/Guardrails/Instructor/PydanticAI basics. Suggested next focus:

1. database schema patterns for case timelines and audit trails
2. FastAPI + SQLAlchemy repository patterns for clean migration
3. UI patterns for timeline/resource matching in case-management products
4. China social-work assessment frameworks and field vocabulary
