# Iteration 010 Research Scan — Redaction Gateway, Prompt Fixtures, and Apply Preview

> Date: 2026-06-21
> Non-repeat rule: this scan does not repeat iteration 001-009. It focuses on redaction evaluation, golden fixtures, prompt regression, and explicit apply-preview workflow after AI draft review.

## 1. Search scope

Platforms and sources checked:

- GitHub/open-source redaction and PII cleaning projects
- LLM prompt regression and evaluation tools
- Stack Overflow / Lobsters / Reddit / Zhihu / TCS Stack Exchange query attempts around redaction tests, prompt fixtures, and review-apply workflows
- Recent research on contextual redaction and prompt testing

High-signal community results for the exact CaseBridge niche remained sparse. Useful patterns came from privacy/redaction benchmarks, prompt testing tools, and LLM application security guidance.

## 2. Findings

### 2.1 Redaction quality must be tested, not assumed

Recent redaction research shows that contextual redaction remains difficult. PII detection is not just entity recognition; whether something should be redacted depends on domain, context, and role.

Decision for CaseBridge:

- Add a redaction gateway wrapper over the current MVP redactor.
- Report residual findings and block provider calls if residual sensitive content remains.
- Keep external providers disabled until redaction gateway is stronger.

### 2.2 Prompt behavior needs golden fixtures

Prompt testing tools and research treat prompts as software artifacts that need regression tests. For CaseBridge, C-0001 should become a golden fixture before prompts or providers change.

Decision for CaseBridge:

- Add a C-0001 intake golden fixture.
- Test that the mock provider produces expected fields.
- Use fixtures before any prompt/provider upgrade.

### 2.3 Apply preview should precede formal apply

A reviewed AI draft still should not directly mutate formal case fields. The safer next step is an apply preview that shows candidate changes and records an audit event, without writing final business fields.

Decision for CaseBridge:

- Add apply-preview endpoint.
- Require AI output review status to be `accepted` or `modified` before preview.
- Make preview state explicit: `will_write_formal_fields=false`.

## 3. Applied decisions in this iteration

Implemented:

- `redaction_gateway.py`
- residual sensitive-content report
- AI intake route uses redaction gate
- C-0001 golden intake fixture
- apply-preview repository function
- apply-preview API route
- AI review UI apply-preview action
- tests for redaction report, golden fixture, and preview gate

## 4. Next design implications

Next version should focus on:

- explicit formal apply endpoint design
- formal assessment table or assessment draft target
- audit event for real apply
- stronger redaction evaluation fixtures
- provider config with safe environment defaults

## 5. Non-repeat rule for next research

Next iteration must not repeat redaction-gateway or prompt-fixture basics. Suggested next focus:

1. Chinese elderly-service assessment dimensions
2. assessment data model and formal apply target fields
3. RBAC and reviewer roles for AI apply workflow
4. redaction failure UX and social-worker remediation flow
