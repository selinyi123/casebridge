# Iteration 007 Research Scan — AI Draft Review Workflow and Human Feedback

> Date: 2026-06-21
> Non-repeat rule: this scan does not repeat iteration 001-006. It focuses on AI draft review, human feedback, annotation/approval queues, LLM observability, and provenance patterns needed before CaseBridge introduces AI intake.

## 1. Search scope

Platforms and sources checked:

- GitHub/open-source references for AI review and feedback workflows
- public references for human-in-the-loop annotation systems
- public references for LLM observability and trace/provenance systems
- Reddit/X/Zhihu query attempts around LLM review queues and human feedback workflows

High-signal Reddit/X/Zhihu results for the exact CaseBridge niche remained sparse. Useful references came from general LLMOps, annotation, and feedback infrastructure.

## 2. Findings

### 2.1 Annotation/review systems separate machine suggestion from human decision

Open-source annotation and labeling systems such as Label Studio, Argilla, CVAT, and related tools show a common pattern: machine suggestions may accelerate work, but the review interface and human confirmation layer remain separate from the model output.

Value for CaseBridge:

- AI intake should create a draft object, not mutate formal case records.
- The UI should show accept / modify / reject actions.
- Review actions should write audit events.
- Human review output should be stored separately from raw model output.

Decision:

- Implement `ai_outputs` with `review_status` before any formal field write path.
- Do not reuse annotation platforms directly; CaseBridge needs domain-specific review wording and privacy controls.

References:

- https://github.com/HumanSignal/label-studio
- https://github.com/argilla-io/argilla
- https://github.com/cvat-ai/cvat

### 2.2 LLM observability systems emphasize traces, prompts, versions, and feedback

Langfuse and similar open-source LLM engineering tools show the need to track prompts, outputs, traces, model versions, and feedback. For CaseBridge, this is important because social-work records need reviewability and explainability.

Value for CaseBridge:

- Store provider name, prompt version, model name, raw output, parsed output, and validation result.
- Keep a trace ID or task ID for each AI attempt.
- Link AI outputs to case notes and audit events.

Decision:

- Add `ai_tasks` and `ai_outputs` instead of writing AI fields directly to case tables.
- Keep provider mocked first.

References:

- https://github.com/langfuse/langfuse
- https://opentelemetry.io/docs/specs/semconv/gen-ai/

### 2.3 LLM-as-judge is not a replacement for professional review

LLM-as-judge and evaluator models are useful for regression testing and model-quality feedback, but they are not a substitute for a professional social-worker review in this project.

Value for CaseBridge:

- Automated evaluation can later check schema quality and hallucination risk.
- Human professional review remains required for any case-facing conclusion.

Decision:

- `v0.1.6` should use schema validation and a mock provider only.
- No LLM judge should approve AI drafts automatically.

References:

- https://en.wikipedia.org/wiki/LLM-as-a-Judge
- https://arxiv.org/abs/2310.08491

## 3. Applied decisions in this iteration

Implemented:

- standalone unified timeline page at `/clients/c-0001/timeline`
- timeline/audit backend retained from previous node
- v0.1.6 plan kept focused on AI intake gate, not full AI automation

## 4. Design implications for next version

Next version should implement:

- `ai_tasks` model
- `ai_outputs` model
- mock provider
- typed intake schema
- redaction before model call
- review states: pending / accepted / modified / rejected
- audit events for AI draft creation and human review
- frontend AI draft panel

## 5. Non-repeat rule for next research

Next iteration must not repeat general annotation/observability basics. Suggested next focus:

1. China social-work elderly assessment dimensions
2. safety taxonomy for AI case-note extraction
3. prompt/version registry design for regulated workflows
4. model-provider abstraction for self-hosted vs external LLMs
