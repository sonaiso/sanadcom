# Governance Constitution Contracts

This package defines constitutional data contracts only.

Scope of this layer:
- structured constitutional entities (`OriginNode`, `BranchLicense`, `EvidenceTrace`, `ConstitutionalDecision`, `GovernedAssessmentDecision`)
- governed enums and validation helpers
- contract-level constraints and tests

Out of scope in this package:
- no AI decision engine
- no automatic compliance judgment
- no metric-to-compliance shortcut behavior

All future NCA, GRC, metrics, evidence, and AI decision paths must consume these contracts before producing any delivery decision.
