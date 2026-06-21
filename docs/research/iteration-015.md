# Iteration 015 Research Scan

Date: 2026-06-21

Focus: service plan to intervention to outcome evidence chain.

## Findings

- Project/workflow systems such as OpenProject, Redmine, Trac, and Request Tracker show useful patterns for work packages, status, role control, evidence, and timeline history.
- CaseBridge should not become a ticket tracker, but it can use a similar chain: plan -> intervention -> outcome -> evidence.
- Human-service open-source work remains sparse; evidence objects should therefore be simple, auditable, and manually controlled.
- Outcome records must stay manual-only; AI should not score or close cases.

## Applied decisions

Implemented:

- ServicePlan model
- ServiceIntervention model
- service plan repository
- service plan migration
- goals router endpoints for plans, interventions, and evidence chain
- evidence chain web view
- repository test for manual evidence chain

## Next

- add service plan timeline integration
- add plan/intervention creation UI
- add supervisor review panel
- add closure readiness check
