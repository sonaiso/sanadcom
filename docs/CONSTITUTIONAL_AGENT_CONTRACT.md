# Constitutional Agent Contract

## Mandatory contract for every agent

- `AGENTS.md` is mandatory and is the root local repository constitution.
- Agent-specific instructions may add stricter constraints but may never remove constitutional constraints.
- No generated PR may introduce direct decision shortcuts from requirement, metric, evidence, RAG output, LLM output, or user assertion to compliance judgment/action.
- No generated PR may convert candidate output into action without the governed transition chain.
- No generated PR may claim NCA approval/certification unless an official certification artifact exists.
- Every governance-sensitive PR must include tests proving no shortcut path occurred.

## Required governed transition chain

Origin → Licensed Branch → Effective Attribute → Sabab/Cause → Condition → Mani/Blocker → Qadih Difference → Evidence Trace → Rank → Residuals → Handoff Rule → Final Delivery Decision

## Examples

Bad:

```python
action_allowed = True
status = "compliant"
```

Good:

```python
decision = constitutional_engine.evaluate(candidate)
action_allowed = decision.action_allowed
rank = decision.rank
residuals = decision.residuals
handoff = decision.handoff
```

Bad:

```python
metric_score >= 85 -> compliant
```

Good:

```python
metric_score -> evidence_candidate
evidence_candidate -> rank policy
rank policy + residuals + blockers -> governed decision
```
