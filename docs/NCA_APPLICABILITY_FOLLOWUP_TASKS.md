# NCA Applicability Follow-up Tasks

This document defines the lightweight follow-up planner after PR #92.

PR #92 separated out-of-scope from blocked/conflict applicability behavior:
- out_of_scope is an operational scope outcome, not a blocked branch.
- conflict is reserved for in-scope contradictions and blockers.

## Constitutional boundary for this layer

This layer does not issue a compliance judgment.
It does not validate evidence sufficiency.
It does not act as an action gateway.
It only maps applicability outcomes to follow-up task candidates.

## Applicability-to-follow-up mapping

- `branch_out_of_scope`
  - No failure state.
  - No required follow-up task.
  - Any qadiḥ differences are retained as audit notes only.
  - qadiḥ differences in out-of-scope do not force human review.

- `branch_in_scope`
  - Ready for the next implementation-focused stage.
  - No required follow-up task.

- `branch_needs_scoping`
  - Generates a `scoping_request` follow-up task.
  - Missing scoping conditions become required inputs.

- `branch_scope_conflict`
  - Generates a `scope_conflict_review` follow-up task.
  - Active maniʿ and qadiḥ differences are captured for audit-oriented review.

## What comes next

The next stage should be implementation-oriented maturity work (for example Evidence Maturity or Implementation Assessment), not a direct decision bridge from applicability.
