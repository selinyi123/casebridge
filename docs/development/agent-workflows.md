# CaseBridge Agent Workflow Operating Model

## Purpose

This document defines how AI-assisted project work should be decomposed when iterating CaseBridge.

The workflow is for development assistance only. It does not authorize AI to write formal case data, close cases, score outcomes, or make social-work decisions.

## Agent roles

1. Research Agent
   - Search public references and reusable open-source patterns.
   - Avoid repeating prior research topics.
   - Output: short evidence-backed notes and non-goals.

2. Product Agent
   - Convert research into a bounded version scope.
   - Preserve CaseBridge rules: human responsibility, manual-only formal writes, privacy first.
   - Output: version acceptance criteria.

3. Implementation Agent
   - Add the smallest useful backend/frontend/docs patch.
   - Prefer existing routers and repositories over new framework layers.
   - Output: committed code.

4. Review Agent
   - Check role boundaries, audit trail, manual-only behavior, and data isolation.
   - Output: risks, limitations, and required follow-up fixes.

5. QA Agent
   - Add repository or route tests when safe.
   - Confirm what was actually tested and what was not tested.
   - Output: test files and CI status notes.

## Standard iteration flow

1. Research non-repeated references.
2. Select one bounded version node.
3. Implement model/repository/API before UI.
4. Add audit event for formal business writes.
5. Add UI only after backend exists.
6. Add tests or explicitly document why not.
7. Update README/checklist.
8. Report completed, blocked, and next-node work.

## Hard stops

- No AI automatic closure.
- No AI automatic risk classification.
- No AI automatic service plan creation.
- No AI automatic intervention creation.
- No AI automatic outcome scoring.
- No formal write without authenticated human actor.
