# Iteration 008 Research Scan — AI Intake Gate Implementation

> Date: 2026-06-21
> Non-repeat rule: this scan does not repeat iteration 001-007. It focuses on the practical implementation of the first AI feature: mock provider, structured output, review state, prompt/provider traceability, and AI-output provenance.

## 1. Search scope

Platforms and sources checked:

- GitHub/open-source LLM observability and feedback systems
- Stack Overflow query attempts around structured output validation and review-state patterns
- Lobsters query attempts around LLM traces, prompts, and observability
- Theoretical Computer Science Stack Exchange query attempts around provenance/audit ideas
- Reddit/X/Zhihu query attempts around AI review queues and human-in-the-loop workflows

High-signal discussion on the exact CaseBridge niche remains sparse across community platforms. The useful patterns are general LLMOps and human-review infrastructure patterns, adapted to social-work constraints.

## 2. Findings

### 2.1 LLM observability: trace prompts, outputs, and feedback

LLM observability tools such as Langfuse show a common architecture: capture traces, prompts, generations, model metadata, evaluations, and feedback. For CaseBridge, this supports the `ai_tasks` and `ai_outputs` split.

Value for CaseBridge:

- Store provider, prompt version, capability, note id, case id, raw output, parsed output, validation status, and review status.
- Link each AI attempt to audit events.
- Never let AI output bypass formal review.

Decision:

- Implement `ai_tasks` and `ai_outputs` now.
- Keep provider mocked until persistence, schema validation, and review flow are tested.

### 2.2 Human review is part of the product, not a later admin feature

Human-in-the-loop NLP and annotation work shows that feedback, review, and correction are workflow primitives. In CaseBridge, review is not optional because AI drafts may affect sensitive service work.

Value for CaseBridge:

- The UI must support accept/reject/modify states.
- Review action should be audited.
- Formal records should not change just because a draft was accepted; that mapping must be a separate explicit operation in a later version.

Decision:

- Implement review status now.
- Keep formal field application out of scope for v0.1.6.

### 2.3 Mock provider first

Adding real model providers too early would make debugging harder and create privacy risk. A deterministic mock provider lets the team test data flow, audit events, redaction, and review states before external calls exist.

Decision:

- `v0.1.6` uses only mock intake provider.
- Real providers are blocked until model abstraction, environment configuration, and production redaction are stronger.

## 3. Applied decisions in this iteration

Implemented:

- `AiTask` model
- `AiOutput` model
- AI task/output migration
- intake draft schema
- mock intake provider
- AI intake route
- AI output review route
- audit events for AI draft creation and review
- AI draft review page
- tests for draft-only behavior and review-state update

## 4. Next design implications

Next version should focus on:

- provider abstraction interface
- prompt registry and prompt versioning
- formal apply/reject/modify workflow design
- stronger redaction service planning
- UI copy and review ergonomics

## 5. Non-repeat rule for next research

Next iteration must not repeat generic human-review or LLM observability basics. Suggested next focus:

1. prompt registry/versioning for regulated workflows
2. China-localized social-work elderly assessment dimensions
3. structured risk-clue extraction taxonomy
4. privacy-preserving provider selection: self-hosted vs external LLM
