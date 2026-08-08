from dataclasses import dataclass, field

from .enums import (
    ConstitutionalRank,
    EngineType,
    ProtocolStage,
    RelationType,
    ResidualKind,
    TransitionStatus,
)


@dataclass(frozen=True)
class RelationProposal:
    relation_type: RelationType
    source_refs: tuple[str, ...]
    target_ref: str
    arity: int = 2

    def __post_init__(self) -> None:
        if not self.source_refs:
            raise ValueError("source_refs are required")
        if not self.target_ref or not self.target_ref.strip():
            raise ValueError("target_ref is required")
        if self.arity < 1:
            raise ValueError("arity must be >= 1")


@dataclass(frozen=True)
class ScopeProfile:
    quantifier: str | None = None
    temporal: str | None = None
    spatial: str | None = None
    conditional: str | None = None
    referential: str | None = None
    modal: str | None = None


@dataclass(frozen=True)
class TransitionProposal:
    proposal_id: str
    proposer_type: EngineType
    source_refs: tuple[str, ...]
    target_candidate_ref: str
    proposed_relation: RelationProposal
    domain_ref: str | None
    scope_ref: str | None
    constitutive_evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    supporting_evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    proposed_rank: ConstitutionalRank = ConstitutionalRank.CANDIDATE
    trace_id: str = ""

    def __post_init__(self) -> None:
        if not self.proposal_id or not self.proposal_id.strip():
            raise ValueError("proposal_id is required")
        if not self.source_refs:
            raise ValueError("source_refs are required")
        if not self.target_candidate_ref or not self.target_candidate_ref.strip():
            raise ValueError("target_candidate_ref is required")
        if not self.trace_id or not self.trace_id.strip():
            raise ValueError("trace_id is required")


@dataclass(frozen=True)
class UnitCertificate:
    certificate_id: str
    carrier_ref: str
    boundary_rule: str
    unit_criterion: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.certificate_id or not self.certificate_id.strip():
            raise ValueError("unit certificate_id is required")
        if not self.carrier_ref or not self.carrier_ref.strip():
            raise ValueError("carrier_ref is required")


@dataclass(frozen=True)
class IdentityCertificate:
    certificate_id: str
    source_ref: str
    target_ref: str
    preserved: bool
    basis: str
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.certificate_id or not self.certificate_id.strip():
            raise ValueError("identity certificate_id is required")
        if not self.source_ref or not self.source_ref.strip():
            raise ValueError("identity source_ref is required")
        if not self.target_ref or not self.target_ref.strip():
            raise ValueError("identity target_ref is required")
        if not self.basis or not self.basis.strip():
            raise ValueError("identity basis is required")


@dataclass(frozen=True)
class DomainContract:
    domain_id: str
    unit_types: tuple[str, ...]
    identity_policy_ref: str
    allowed_relation_types: tuple[RelationType, ...]
    allowed_operation_types: tuple[str, ...]
    evidence_policy_ref: str
    scope_policy_ref: str
    rank_policy_ref: str

    def __post_init__(self) -> None:
        if not self.domain_id or not self.domain_id.strip():
            raise ValueError("domain_id is required")
        if not self.allowed_relation_types:
            raise ValueError("allowed_relation_types are required")


@dataclass(frozen=True)
class RelationCertificate:
    certificate_id: str
    relation_type: RelationType
    arity: int
    direction: str
    source_roles: tuple[str, ...]
    target_roles: tuple[str, ...]
    preconditions: tuple[str, ...] = field(default_factory=tuple)
    blockers: tuple[str, ...] = field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.certificate_id or not self.certificate_id.strip():
            raise ValueError("relation certificate_id is required")
        if self.arity < 1:
            raise ValueError("relation arity must be >= 1")


@dataclass(frozen=True)
class ScopeCertificate:
    certificate_id: str
    supported_scope: ScopeProfile
    certified_scope: ScopeProfile
    generalization_license: bool = False

    def __post_init__(self) -> None:
        if not self.certificate_id or not self.certificate_id.strip():
            raise ValueError("scope certificate_id is required")


@dataclass(frozen=True)
class ClosureBundle:
    structural: bool
    referential: bool
    inferential: bool
    epistemic: bool


@dataclass(frozen=True)
class Residual:
    code: str
    kind: ResidualKind
    stage: ProtocolStage
    description: str
    blocking: bool = True
    rank_ceiling: ConstitutionalRank = ConstitutionalRank.ASSURED
    trace_ref: str = ""
    reopen_condition: str = ""

    def __post_init__(self) -> None:
        if not self.code or not self.code.strip():
            raise ValueError("residual code is required")
        if not self.description or not self.description.strip():
            raise ValueError("residual description is required")
        if not self.trace_ref or not self.trace_ref.strip():
            raise ValueError("residual trace_ref is required")
        if not self.reopen_condition or not self.reopen_condition.strip():
            raise ValueError("residual reopen_condition is required")


@dataclass(frozen=True)
class TransitionCertificate:
    proposal_id: str
    unit_certificate_id: str
    identity_certificate_id: str
    domain_id: str
    relation_certificate_id: str
    scope_certificate_id: str
    closure_bundle: ClosureBundle
    residual_ids: tuple[str, ...]
    certified_rank: ConstitutionalRank
    decision: TransitionStatus
    constitution_version: str
    trace_id: str
    reopen_conditions: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.proposal_id or not self.proposal_id.strip():
            raise ValueError("proposal_id is required")
        if not self.unit_certificate_id or not self.unit_certificate_id.strip():
            raise ValueError("unit_certificate_id is required")
        if not self.identity_certificate_id or not self.identity_certificate_id.strip():
            raise ValueError("identity_certificate_id is required")
        if not self.domain_id or not self.domain_id.strip():
            raise ValueError("domain_id is required")
        if not self.relation_certificate_id or not self.relation_certificate_id.strip():
            raise ValueError("relation_certificate_id is required")
        if not self.scope_certificate_id or not self.scope_certificate_id.strip():
            raise ValueError("scope_certificate_id is required")
        if not self.trace_id or not self.trace_id.strip():
            raise ValueError("trace_id is required")
        if not self.reopen_conditions:
            raise ValueError("reopen_conditions are required")


@dataclass(frozen=True)
class ProtocolDecision:
    status: TransitionStatus
    failed_stage: ProtocolStage | None
    certified_rank: ConstitutionalRank
    rank_ceiling: ConstitutionalRank
    residuals: tuple[Residual, ...]
    transition_certificate: TransitionCertificate | None
