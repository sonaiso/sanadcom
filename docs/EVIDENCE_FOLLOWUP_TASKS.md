# Evidence Follow-up Tasks

This layer is workflow planning only.

It converts evidence maturity gaps into follow-up task candidates that can be executed later by the right owner.

## Constitutional boundaries

- This layer does not produce a compliance judgment.
- This layer does not produce an action gate.
- This layer does not produce approval or certification statements.
- `evidence_validated` remains an internal maturity state only and is not a compliance outcome.

## State-to-task mapping

- `evidence_missing` → `evidence_request`
- `evidence_draft` → `submit_evidence_task`
- `evidence_submitted` → `owner_attestation_task`
- `evidence_attested` → `reviewer_validation_task`
- `evidence_expired` → `evidence_refresh_task`
- `evidence_rejected` → `corrective_evidence_task`
- `evidence_conflicting` → `audit_review_task`
- `evidence_validated` → `no_followup_required`

## Operational purpose

This planner answers operational questions without crossing into compliance decisions:

- what is the next task?
- who should pick it up?
- which inputs are missing?
- does the state block validation?
- does the state require human review?
