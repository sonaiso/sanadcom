# NCA Evidence Trace Boundary

This document defines the constitutional boundary between NCA branch applicability and evidence-trace handling.

## Position in governed flow

Origin → Branch Applicability → Evidence Trace → Rank → Residuals → Handoff / Delivery Decision

Evidence trace binding starts only after branch applicability is evaluated.
It is a governed input stage, not a compliance judgment stage.

## Evidence trace contract

Mandatory evidence trace fields:

- `source`
- `scope`
- `owner`
- `freshness`
- `control_binding`

Optional supporting references may include:

- `artifact_ref`
- `evidence_ref`
- `evidence_type`
- `metric_like`

`source` is the canonical evidence origin field for this layer.

## Boundary rules

- applicability output must not emit compliance, approval, certification, or `action_allowed`
- evidence trace completeness must not be treated as control verification by itself
- evidence trace evaluation may produce residuals but must not bypass rank and handoff stages
- no AI/RAG output may be promoted directly to delivery decision
