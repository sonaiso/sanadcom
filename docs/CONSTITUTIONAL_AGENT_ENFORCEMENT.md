# Constitutional Agent Enforcement

## Why AGENTS.md is mandatory
`AGENTS.md` is the binding constitutional contract for this repository. It defines the governed transition chain and blocks shortcut jumps from candidate inputs to compliance decisions.

## Expected compliance for agents and contributors
Copilot, Claude, Codex, automation scripts, and human contributors must read and follow `AGENTS.md` before modifying governance-sensitive logic. Every decision path must preserve:

Origin → BranchLicense → Effective Attribute → Sabab → Conditions → Mani/Blockers → Qadih Differences → Evidence Trace → Rank → Residuals → Handoff/Delivery.

## What the CI checker blocks
`scripts/check_constitutional_compliance.py` fails CI when:
- Required constitutional governance files are missing.
- `AGENTS.md` loses mandatory constitutional terms.
- Agent instruction files stop requiring read/follow behavior for `AGENTS.md`.
- Runtime code introduces explicit bypass tokens (skip/bypass/force-allow patterns).
- Governance-sensitive runtime paths assign compliant/allowed/verified outcomes directly without constitutional guard references.
- Content claims NCA official certification/approval wording.

## Forbidden jumps
The checker is designed to detect and block common shortcut patterns, including:
- requirement → compliant
- metric → compliant
- evidence attachment → verified
- policy text → implementation proof
- RAG output → decision
- LLM output → action or decision
- score → compliance

## Safe way to add new GRC/NCA/evidence/metric/AI logic
1. Keep decisions governed by the constitutional transition chain.
2. Use explicit transition evaluation and decision objects.
3. Keep rank bounded by evidence quality and trace completeness.
4. Emit residuals for failed/deferred paths.
5. Route unresolved paths to deferral or human review handoff.
6. Add constitutional tests for blocked and allowed paths.

## Exception handling rule
Exceptions must be modeled as explicit governed outcomes (for example `SecurityException`, residual entries, deferred decision, or human handoff). Exceptions must not be implemented as bypass flags or shortcut allow paths.

## NCA wording rule
Sanadcom may be described as NCA-aligned, NCA-mapped, or evidence-ready. It must not be described as NCA-certified or officially approved unless formal certification evidence exists.
