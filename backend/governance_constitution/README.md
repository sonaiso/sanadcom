# Governance Constitution Contracts

This package defines governance constitutional data contracts as a dependent application.

Scope of this layer:
- structured constitutional entities (`OriginNode`, `BranchLicense`, `EvidenceTrace`, `ConstitutionalDecision`, `GovernedAssessmentDecision`)
- governance application entrypoint consuming approved knowledge context (`evaluate_governance_application`)
- governed enums and validation helpers
- contract-level constraints and tests
- governed delivery payload export (`GovernedAssessmentDecision.to_delivery_payload`) containing candidate, origin, branch, effective attribute, sabab, conditions, mani, qadih differences, evidence traces, rank, residuals, and delivery decision

Out of scope in this package:
- no AI decision engine
- no automatic compliance judgment
- no metric-to-compliance shortcut behavior

All future NCA, GRC, metrics, evidence, and AI decision paths must consume these contracts before producing any delivery decision.
This package must consume `knowledge_constitution` approved context and must not fabricate upstream locus/domain/claim/evidence-binding proofs internally.
