# Sanadcom Knowledge Constitution

## 0. Constitutional Status

This document is the supreme knowledge constitution of Sanadcom.

It governs every representation, assessment, compliance evaluation, risk evaluation, evidence evaluation, AI output, metric interpretation, report, recommendation, workflow transition, delivery decision, and executable action in this repository.

`governance_constitution` is a dependent application of this constitution for governance, risk, compliance, cybersecurity, assurance, and regulatory domains. It is not the supreme epistemic core.

No lower-level instruction, model output, workflow, metric, or implementation may override this document.

## 1. Foundational Identity

Sanadcom is a governed knowledge-transition system. It does not grant compliance, assurance, or executable authority directly from requirements, documents, metrics, scores, RAG outputs, or LLM outputs.

Every candidate must move through licensed stages:

Reality -> Trace -> Distinction -> Definition -> Locus -> Boundary -> Domain -> Claim -> Relation -> Evidence Binding -> Rank -> Residuals -> Judgment Candidate -> Action License -> Feedback Trace.

No judgment or action is licensed before locus, boundaries, domain, claim, relation, and evidence path are established.

## 2. Supreme Law

The default state of every stage transition is prohibited.
A transition is allowed only by an explicit transition license preserving:

- source stage and target stage
- preserved identity
- defined locus and bounded domain
- valid relation and appropriate evidence trace
- conditions and operative reason (sabab)
- absence of active blockers (mani)
- declared material differences (qadih)
- rank ceiling bounded by evidence
- recorded residuals
- complete transition trace
- declared transition effect

## 3. Constitutional Distinctions

The following distinctions must never be collapsed:

- reality vs representation
- trace vs claim
- claim vs evidence
- evidence vs proof
- proof vs rank
- rank vs judgment
- judgment vs action
- action vs feedback effect in reality
- normative requirement vs applicability
- applicability vs satisfaction
- out-of-scope vs in-scope failure
- exception vs compliance

## 4. Core Constitutional Objects

Minimum constitutional objects:

- `RealityCandidate`
- `TraceCandidate`
- `DefinedLocus`
- `DomainContract`
- `ClaimCandidate`
- `RelationCandidate`
- `NormativeSource` (when applicable)
- `ApplicabilityCandidate` (when applicable)
- `EvidenceBinding`
- `Rank`
- `Residual`
- `JudgmentCandidate`
- `ActionLicense`
- `FeedbackTrace`

## 5. Knowledge Transition Chain

Required chain for executable implementations:

1. `RealityCandidate`
2. `TraceCandidate`
3. `DefinedLocus`
4. `DomainContract`
5. `ClaimCandidate`
6. `RelationCandidate`
7. `EvidenceBinding`
8. `RankAssignment`
9. `ResidualAudit`
10. `JudgmentCandidate`
11. `ActionLicense`
12. `Handoff/Delivery`
13. `FeedbackTrace`
14. `Reality Re-evaluation`

Implementations may add stricter intermediate stages but may not remove mandatory distinctions.

## 6. No-Jump Laws

- No trace directly becomes a fact.
- No document directly becomes proof.
- No requirement directly becomes applicability.
- No applicability directly becomes compliance.
- No policy directly verifies a control.
- No metric directly becomes a judgment.
- No score directly becomes assurance.
- No citation directly establishes truth.
- No RAG result directly becomes a judgment.
- No LLM output directly becomes a decision.
- No AI confidence directly raises rank.
- No branch license may operate before locus and domain are established.
- No evidence may be evaluated without a claim.
- No claim may be judged without relation to a defined locus.
- No rank may exceed the weakest evidence binding.
- No judgment directly becomes an action.
- No action is complete without feedback trace.

## 7. Governance Constitution as Dependent Application

`backend/governance_constitution` is a domain application under this constitution.

- `OriginNode` is a governance `NormativeSource` representation.
- `BranchLicense` is a governance applicability license.
- `EvidenceTrace` is a trace input and must participate in `EvidenceBinding`.
- `ConstitutionalDecision` is a governance judgment candidate.
- `HandoffRule` and `action_allowed` are action-license concerns.

Governance evaluation must consume an approved knowledge context and may not fabricate upstream proofs internally.

## 8. Agent and Automation Governance

`AGENTS.md` and all agent instructions are subordinate to this document.

Agents and automations must:

- preserve candidate status
- declare stage and provenance
- preserve residuals
- respect rank ceilings
- separate judgment from action
- produce feedback trace for material actions

Agents and automations must not:

- self-verify their outputs
- fabricate locus/domain/relation/evidence/rank
- erase counterevidence or suppress residuals
- reinterpret out-of-scope as failure
- describe Sanadcom as certified without certification evidence bound to locus, authority, scope, and time

## 9. Required Decision Envelope

Every governed judgment must provide at least:

- `knowledge_context_id`
- `reality_candidate_id`
- `trace_ids`
- `defined_locus_id`
- `domain_contract_id`
- `claim_id`
- `relation_ids`
- `normative_source_ids` (when applicable)
- `applicability_result` (when applicable)
- `evidence_binding_ids`
- `rank` and `rank_ceiling`
- `failed_stage`
- `residuals`
- `judgment_type` and `judgment_status`
- `action_license`
- `handoff`
- `transition_trace`
- `feedback_requirement`

## 10. Repository Precedence

1. `docs/00_KNOWLEDGE_CONSTITUTION.md`
2. constitutional knowledge contracts and tests
3. `AGENTS.md`
4. `governance_constitution`
5. domain applications (NCA, GRC, AI, metrics, evidence, risk, assessment)
6. workflows, APIs, services, UI, reports, prompts, generated outputs

If rules conflict, precedence goes to the stricter rule that preserves identity, domain boundaries, evidence discipline, rank ceilings, residual visibility, reversibility, and no-jump protection.

## 11. First Implementation Rule

The first implementation must introduce a minimal executable knowledge kernel with both:

- one licensed successful transition
- one failed transition that records residuals and blocks judgment/action

Only after this kernel passes constitutional tests may governance applications consume it.

## 12. Final Governing Principle

Sanadcom preserves the governed path from reality to trace, locus, domain, claim, relation, evidence, rank, residuals, judgment, action, and feedback.

No judgment or action is allowed before stage licensing, boundary discipline, and full transition trace are satisfied.
