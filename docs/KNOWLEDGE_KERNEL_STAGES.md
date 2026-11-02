# Knowledge kernel: stages 11–14 and the added gates

Scope: `backend/knowledge_constitution`. This note records what the kernel now enforces, so that every
gate can be traced to a sentence of `docs/00_KNOWLEDGE_CONSTITUTION.md`.

## Gates added to `evaluate_knowledge_transition` (stages 1–10)

| Residual code | Stage | Constitutional sentence |
|---|---|---|
| `unresolved_identity_residuals` | REALITY_CANDIDATE | §2 "preserved identity" |
| `trace_reality_mismatch` | TRACE_CANDIDATE | §3 "trace vs claim"; a trace observes one reality |
| `locus_reality_mismatch`, `unresolved_boundary_residuals` | DEFINED_LOCUS | §1 "No judgment … before locus, boundaries … are established" |
| `claim_relation_not_admissible` | CLAIM_CANDIDATE | §2 "valid relation" under the domain contract |
| `missing_relation_candidates`, `relation_unanchored` | RELATION_CANDIDATE | §6 "No claim may be judged without relation to a defined locus" |
| `relation_domain_mismatch`, `relation_type_not_admissible`, `relation_trace_missing` | RELATION_CANDIDATE | §2 "bounded domain", "appropriate evidence trace" |
| rank ceiling CANDIDATE when a bound trace has broken provenance or integrity | RANK_ASSIGNMENT | §6 "No rank may exceed the weakest evidence binding" |

`failed_stage` is always the earliest failed stage, in chain order.

## Stages 11–14 (`action.py`)

- `evaluate_action_license(context, …) -> ActionDecision`: a licence is **granted only if** the judgment is approved,
  no blocking residual remains, `min(rank, rank_ceiling) ≥ minimum_rank`, and no active blocker (maniʿ) is declared.
  Default `minimum_rank` is VERIFIED. Blockers are supplied by the caller; absence is never read as inactivity.
- Handoff routes: `AUTOMATION` (granted), `DEFERRAL_QUEUE` (approved but rank below threshold), `HUMAN_REVIEW` (anything else).
- A granted licence carries a `FeedbackRequirement`; `record_feedback` accepts a `FeedbackTrace` only if it names the same
  licence and the same reality candidate, and then yields a new `RealityCandidate` (stage 14). The re-evaluated reality is a
  candidate again; it inherits no rank from the action.
- `decision_envelope(context, action=None)` projects the §9 envelope. When the action stage was not evaluated, its three
  keys are `None`, so a missing stage is visible rather than implied.

## What is deliberately not here

- No wiring into Django models, APIs or the UI: the kernel stays a pure, testable core (§11 "First Implementation Rule").
- No NCA/ECC-specific logic: that remains in `governance_constitution`, which consumes an approved context.
- Nothing here produces a compliance judgment about a framework control, and nothing may be read as certification.
