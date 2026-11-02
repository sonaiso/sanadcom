from dataclasses import dataclass, field

from .enums import HandoffRoute, JudgmentStatus, KnowledgeRank, KnowledgeStage


@dataclass(frozen=True)
class RealityCandidate:
    reality_candidate_id: str
    reality_type: str
    temporal_bounds: str
    observation_source: str
    identity_conditions: tuple[str, ...] = field(default_factory=tuple)
    unresolved_identity_residuals: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.reality_candidate_id.strip():
            raise ValueError("reality_candidate_id is required")
        if not self.reality_type.strip():
            raise ValueError("reality_type is required")


@dataclass(frozen=True)
class TraceCandidate:
    trace_id: str
    reality_candidate_id: str
    source: str
    scope: str
    owner: str
    freshness: str
    control_binding: str
    trace_type: str = "documentary"
    provenance_ok: bool = True
    integrity_ok: bool = True
    transformation_history: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        required = {
            "trace_id": self.trace_id,
            "reality_candidate_id": self.reality_candidate_id,
            "source": self.source,
            "scope": self.scope,
            "owner": self.owner,
            "freshness": self.freshness,
            "control_binding": self.control_binding,
        }
        for name, value in required.items():
            if not value or not value.strip():
                raise ValueError(f"{name} is required")


@dataclass(frozen=True)
class DefinedLocus:
    defined_locus_id: str
    locus_type: str
    reality_candidate_id: str
    boundaries: str
    applicable_time: str
    identity_evidence: tuple[str, ...] = field(default_factory=tuple)
    boundary_residuals: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.defined_locus_id.strip():
            raise ValueError("defined_locus_id is required")
        if not self.reality_candidate_id.strip():
            raise ValueError("reality_candidate_id is required")


@dataclass(frozen=True)
class DomainContract:
    domain_contract_id: str
    governing_vocabulary: str
    admissible_relation_types: tuple[str, ...]
    evidence_rules: tuple[str, ...]
    rank_policy: str

    def __post_init__(self) -> None:
        if not self.domain_contract_id.strip():
            raise ValueError("domain_contract_id is required")


@dataclass(frozen=True)
class ClaimCandidate:
    claim_id: str
    defined_locus_id: str
    predicate: str
    relation_type: str
    temporal_scope: str
    domain_contract_id: str
    required_evidence_class: str

    def __post_init__(self) -> None:
        required = {
            "claim_id": self.claim_id,
            "defined_locus_id": self.defined_locus_id,
            "predicate": self.predicate,
            "relation_type": self.relation_type,
            "domain_contract_id": self.domain_contract_id,
        }
        for name, value in required.items():
            if not value or not value.strip():
                raise ValueError(f"{name} is required")


@dataclass(frozen=True)
class RelationCandidate:
    relation_id: str
    source_object_id: str
    target_object_id: str
    relation_type: str
    domain_contract_id: str
    evidence_trace_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.relation_id.strip():
            raise ValueError("relation_id is required")


@dataclass(frozen=True)
class EvidenceBinding:
    evidence_binding_id: str
    claim_id: str
    defined_locus_id: str
    domain_contract_id: str
    trace_ids: tuple[str, ...]
    provenance_ok: bool = True
    integrity_ok: bool = True
    scope_coverage_ok: bool = True
    temporal_coverage_ok: bool = True
    claim_relevance_ok: bool = True

    def __post_init__(self) -> None:
        required = {
            "evidence_binding_id": self.evidence_binding_id,
            "claim_id": self.claim_id,
            "defined_locus_id": self.defined_locus_id,
            "domain_contract_id": self.domain_contract_id,
        }
        for name, value in required.items():
            if not value or not value.strip():
                raise ValueError(f"{name} is required")
        if not self.trace_ids:
            raise ValueError("trace_ids are required")


@dataclass(frozen=True)
class Residual:
    failed_stage: KnowledgeStage
    code: str
    description: str
    blocking: bool = True

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("residual code is required")
        if not self.description.strip():
            raise ValueError("residual description is required")


@dataclass(frozen=True)
class JudgmentCandidate:
    judgment_type: str
    judgment_status: JudgmentStatus
    rank: KnowledgeRank
    failed_stage: KnowledgeStage | None
    residuals: tuple[Residual, ...]


@dataclass(frozen=True)
class ApprovedKnowledgeContext:
    knowledge_context_id: str
    reality_candidate: RealityCandidate
    trace_candidates: tuple[TraceCandidate, ...]
    defined_locus: DefinedLocus
    domain_contract: DomainContract
    claim_candidate: ClaimCandidate
    relation_candidates: tuple[RelationCandidate, ...]
    evidence_bindings: tuple[EvidenceBinding, ...]
    rank: KnowledgeRank
    rank_ceiling: KnowledgeRank
    failed_stage: KnowledgeStage | None
    residuals: tuple[Residual, ...]
    judgment_candidate: JudgmentCandidate
    approved: bool
    transition_trace: tuple[KnowledgeStage, ...]


@dataclass(frozen=True)
class ActionLicense:
    """Stage 11: a licence to act is distinct from a judgment and is never implied by one."""

    action_license_id: str
    knowledge_context_id: str
    action_type: str
    minimum_rank: KnowledgeRank
    rank_at_licensing: KnowledgeRank
    granted: bool
    failed_stage: KnowledgeStage | None
    residuals: tuple[Residual, ...]

    def __post_init__(self) -> None:
        if not self.action_license_id.strip():
            raise ValueError("action_license_id is required")
        if not self.action_type.strip():
            raise ValueError("action_type is required")


@dataclass(frozen=True)
class HandoffDecision:
    """Stage 12: where the candidate goes next; a route, not an approval."""

    route: HandoffRoute
    owner: str | None
    rationale: str

    def __post_init__(self) -> None:
        if not self.rationale.strip():
            raise ValueError("handoff rationale is required")


@dataclass(frozen=True)
class FeedbackRequirement:
    """Stage 13 obligation: a material action is incomplete until its effect in reality is traced."""

    required: bool
    reality_candidate_id: str
    action_license_id: str | None
    feedback_trace_id: str | None = None


@dataclass(frozen=True)
class FeedbackTrace:
    """Stage 13 record: what the action did in reality, observed, not assumed."""

    feedback_trace_id: str
    action_license_id: str
    reality_candidate_id: str
    observed_effect: str
    observed_at: str
    observation_source: str
    reality_changed: bool

    def __post_init__(self) -> None:
        required = {
            "feedback_trace_id": self.feedback_trace_id,
            "action_license_id": self.action_license_id,
            "reality_candidate_id": self.reality_candidate_id,
            "observed_effect": self.observed_effect,
            "observed_at": self.observed_at,
            "observation_source": self.observation_source,
        }
        for name, value in required.items():
            if not value or not value.strip():
                raise ValueError(f"{name} is required")


@dataclass(frozen=True)
class ActionDecision:
    knowledge_context_id: str
    action_license: ActionLicense
    handoff: HandoffDecision
    feedback_requirement: FeedbackRequirement
    residuals: tuple[Residual, ...]
    failed_stage: KnowledgeStage | None
    transition_trace: tuple[KnowledgeStage, ...]


@dataclass(frozen=True)
class FeedbackResult:
    """Stage 14: the feedback either closes the loop with a new reality candidate or records why it cannot."""

    accepted: bool
    residuals: tuple[Residual, ...]
    failed_stage: KnowledgeStage | None
    reality_reevaluation: RealityCandidate | None
    transition_trace: tuple[KnowledgeStage, ...]
