from dataclasses import dataclass, field

from .enums import JudgmentStatus, KnowledgeRank, KnowledgeStage


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
