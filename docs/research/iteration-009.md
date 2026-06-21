# Iteration 009 Research Scan — Provider Registry and Prompt Versioning

> Date: 2026-06-21
> Non-repeat rule: this scan does not repeat iteration 001-008. It focuses on provider selection, prompt versioning, and redaction gates before any real model provider is enabled.

## 1. Search scope

Platforms and sources checked:

- GitHub/open-source LLM gateway and provider abstraction projects
- prompt testing and prompt-regression research
- Stack Overflow, Lobsters, Reddit, Zhihu, and TCS Stack Exchange query attempts around prompt versioning and provider routing
- recent research on PII redaction and prompt management

High-signal community results for this exact project niche remained sparse. Useful patterns came from LLM gateways, prompt management studies, prompt test tools, and redaction research.

## 2. Findings

### 2.1 Provider abstraction should precede real provider use

LLM gateway projects show a common pattern: route model providers behind one interface and track provider metadata. CaseBridge should not call providers directly from API routes.

Decision:

- Add provider registry.
- Keep only `mock` enabled in v0.1.7.
- Reject unknown providers explicitly.

### 2.2 Prompt versioning should be explicit

Prompt-management research reports maintainability issues such as inconsistent formatting and duplication. For CaseBridge, prompts are workflow artifacts and should be versioned.

Decision:

- Add prompt registry with `intake-v0.1.7`.
- Store prompt version in AI task and audit payloads.
- Make future prompt changes testable.

### 2.3 Redaction remains a gate

PII redaction research shows that redaction quality varies across methods. For CaseBridge, model input must be redacted first, and unknown providers should remain disabled.

Decision:

- Keep mock provider only.
- Record provider and prompt version.
- Do not store raw sensitive note text in audit payloads.

## 3. Applied decisions in this iteration

Implemented:

- `prompt_registry.py`
- `provider_registry.py`
- explicit unknown-provider rejection
- AI intake route uses registry layer
- repository records provider and prompt version in AI task and audit payload
- tests assert provider and prompt version metadata

## 4. Next design implications

Next version should focus on:

- stronger redaction gateway
- prompt test fixtures
- provider configuration through safe defaults
- AI output modification UI
- explicit apply-to-formal-assessment workflow after human review

## 5. Non-repeat rule for next research

Next iteration must not repeat provider abstraction basics. Suggested next focus:

1. Chinese social-work elderly assessment taxonomy
2. prompt regression fixtures and golden cases
3. redaction failure reporting
4. explicit apply workflow after AI review
