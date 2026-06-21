# Iteration 011 Research Scan — Formal Assessment Target and Explicit Apply Workflow

> Date: 2026-06-21
> Non-repeat rule: this scan does not repeat redaction gateway, prompt registry, or apply-preview basics. It focuses on formal assessment targets, provenance, questionnaire/response models, and case-management assessment stages.

## 1. Search scope

Platforms and sources checked:

- GitHub/open-source form and assessment data models
- public references on FHIR resources and QuestionnaireResponse-style structured forms
- public references on case management stages and psychosocial assessment
- Stack Overflow / Lobsters / Reddit / Zhihu / TCS Stack Exchange query attempts around formal apply, assessment targets, provenance, and audit trails

High-signal community discussion for this exact CaseBridge niche remains sparse. Useful patterns came from structured health/social-service records, questionnaire response design, and case-management process literature.

## 2. Findings

### 2.1 Assessment is a first-class stage in case management

Case-management references describe assessment as a stage distinct from intake notes, planning, intervention, monitoring, and review. This supports making `case_assessments` a formal target table instead of treating AI drafts or notes as assessments.

Decision for CaseBridge:

- Add `case_assessments` as a formal target.
- Keep `case_notes`, `ai_outputs`, and `case_assessments` separate.

### 2.2 Structured assessment data needs provenance

Healthcare interoperability patterns such as FHIR emphasize structured resources and source traceability. CaseBridge does not need to implement FHIR now, but it should preserve source note, AI output, provider, prompt version, reviewer, and timestamp.

Decision for CaseBridge:

- Store `source_note_id`, `source_ai_output_id`, `provider`, `prompt_version`, and reviewer fields on assessments.
- Add audit event `ai.output.applied_to_assessment`.

### 2.3 Explicit apply should be different from review

Accepting a draft is not the same as writing a formal assessment. A separate apply step makes responsibility, traceability, and rollback clearer.

Decision for CaseBridge:

- Add explicit apply endpoint.
- Require review status `accepted` or `modified`.
- Require reviewer responsibility confirmation.

## 3. Applied decisions in this iteration

Implemented:

- `CaseAssessment` model
- case assessment migration
- `ApplyAiOutputRequest` schema
- explicit apply-to-assessment repository function
- apply-to-assessment API route
- assessment list API route
- formal assessments web page
- AI review page apply checkbox and action
- tests for pending block, responsibility block, successful apply, source trace, and timeline/audit event

## 4. Next design implications

Next version should focus on:

- assessment schema vocabulary for Chinese elderly social-work service
- assessment edit/version history
- reviewer roles and RBAC
- assessment export/report view
- outcome tracking linked to assessment and service goals

## 5. Non-repeat rule for next research

Next iteration must not repeat formal assessment target basics. Suggested next focus:

1. Chinese elderly-service assessment dimensions
2. outcome tracking and goal-attainment scaling
3. RBAC/reviewer role model
4. assessment versioning and correction workflow
