# Iteration 013 Research Scan

Date: 2026-06-21

Focus: stabilization after outcome tracking, audit trail, RBAC reviewer role, and evidence chain.

## Findings

- RBAC should be introduced as a small reviewer-role gate before complex permissions.
- Audit trail should remain the source of evidence for assessment apply and outcome creation.
- Outcome evidence should be linked to goals or assessments when available, but manual free-standing outcome notes remain useful in MVP.
- Project-management systems such as Redmine/OpenProject are useful references for roles, status objects, workflow, and audit history, but CaseBridge should not become a ticket tracker.

## Applied decisions

Implemented this round:

- outcome migration file
- outcome timeline integration
- schema access alias under outcomes router
- README stabilization status
- tests for outcome timeline and schema alias

## Next

- reviewer role placeholder
- assessment correction/version history
- RBAC route guard skeleton
- outcome report view
- service-plan-to-outcome evidence chain
