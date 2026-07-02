# Sanadcom Constitutional Agent Guard

## Purpose
This repository enforces a constitutional governance contract for all agents, contributors, AI assistants, and automated workflows.

Any agent modifying this repository must treat every framework requirement, metric, evidence item, RAG output, LLM output, assessment score, or automation action as a candidate only.

No candidate may become a compliance judgment, verified control, reportable decision, or executable action unless it passes the Sanadcom constitutional transition:

Origin → Licensed Branch → Effective Attribute → Sabab → Conditions → Maniʿ/Blockers → Qadih Differences → Evidence Trace → Rank → Residuals → Handoff / Delivery Decision.

Violating this rule is a constitutional failure and must be blocked by tests.

## Constitutional laws
1. No branch without an origin.
2. No branch may operate without an explicit BranchLicense.
3. No BranchLicense is valid unless it declares: origin, branch, effective_attribute, sabab, conditions, blockers/maniʿ, qadih_differences, evidence_requirements, rank_policy, residual_policy.
4. No metric is allowed to become a compliance judgment by itself.
5. No evidence attachment is allowed to become proof unless it has trace, scope, owner, freshness, and control binding.
6. No AI output is allowed to become a decision or action without a governed transition decision.
7. No RAG citation is allowed to become a judgment by itself.
8. No control may be marked verified only because a policy exists.
9. No action is allowed when blockers exist or when rank is below the action threshold.
10. Every failed gate must produce residuals and a failed_stage.
11. Every exception must be recorded as an exception, not silently treated as compliance.
12. Every future agent must follow this constitution before modifying GRC, NCA, AI, metrics, evidence, risk, compliance, or assessment logic.

## Forbidden shortcuts
- “policy exists” → “control verified”
- “metric above target” → “compliant”
- “document attached” → “evidence sufficient”
- “RAG found source” → “claim true”
- “LLM answered confidently” → “decision allowed”
- “branch mentioned” → “branch applicable”
- “cloud control” → “critical system control”
- “ECC control” → “DCC/CCC/CSCC/OTCC/TCC satisfied”
- “assessment score” → “delivery decision”
- no shortcut from candidate inputs to final compliance judgment
- no bypass around constitutional transition gates

## No Agent Bypass
No agent may:
- ignore this file,
- weaken the constitution,
- mark its own output as verified,
- create a shortcut from generated output to compliance decision,
- add exception flags that skip constitutional evaluation,
- raise rank above evidence,
- remove residuals to make a decision appear clean,
- describe Sanadcom as NCA-certified unless formal certification evidence exists.

## Required decision object shape
All constitutional decisions must include at least:
- origin
- branch
- BranchLicense reference
- effective_attribute
- sabab
- evaluated conditions
- maniʿ/blockers
- qadih differences
- evidence trace evaluation
- rank
- failed_stage (when not fully allowed)
- residuals
- handoff or delivery decision

## Required behavior before touching GRC/NCA/AI/metrics/evidence code
- Read this file before implementing or reviewing changes.
- Preserve the Origin → BranchLicense → Evidence Trace → Rank transition gates.
- Add or update constitutional tests for any logic affecting GRC, NCA, AI, metrics, evidence, risk, compliance, or assessment flow.
- Record exceptions explicitly; do not silently treat exceptions as compliance.

## Test rule for future PRs
Any PR that modifies GRC logic, NCA applicability, AI assessment flow, metrics interpretation, or evidence evaluation must include constitutional tests that block forbidden conceptual jumps.
