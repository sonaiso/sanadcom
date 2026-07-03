# NCA Lightweight Applicability Semantics

This note clarifies lightweight applicability behavior for NCA branch opening.

## Key rules

- `branch_out_of_scope` is not a failure state.
- `branch_scope_conflict` is not used for simple scope absence.
- missing scope inputs move the branch to `branch_needs_scoping`.

## State intent

- `branch_in_scope`: branch scope exists and required scoping conditions are present.
- `branch_out_of_scope`: no applicable scope signal exists for the branch.
- `branch_needs_scoping`: branch is in scope but required scoping inputs are incomplete.
- `branch_scope_conflict`: branch is in scope but has an explicit scope contradiction or blocker.

## Operational guidance

- Out-of-scope does not imply nonconformity.
- Blockers are reserved for in-scope contradictions, not absent scope.
- `branch_needs_scoping` should generate follow-up tasks in later workflow stages, not compliance judgments.
