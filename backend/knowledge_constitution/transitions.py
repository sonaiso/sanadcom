from .contracts import (
    ApprovedKnowledgeContext,
    ClaimCandidate,
    DefinedLocus,
    DomainContract,
    EvidenceBinding,
    JudgmentCandidate,
    RealityCandidate,
    RelationCandidate,
    Residual,
    TraceCandidate,
)
from .enums import JudgmentStatus, KnowledgeRank, KnowledgeStage
from .rank import binding_rank_ceiling


def evaluate_knowledge_transition(
    *,
    knowledge_context_id: str,
    reality_candidate: RealityCandidate,
    trace_candidates: tuple[TraceCandidate, ...],
    defined_locus: DefinedLocus,
    domain_contract: DomainContract,
    claim_candidate: ClaimCandidate,
    relation_candidates: tuple[RelationCandidate, ...],
    evidence_bindings: tuple[EvidenceBinding, ...],
    requested_rank: KnowledgeRank = KnowledgeRank.SUPPORTED,
) -> ApprovedKnowledgeContext:
    residuals: list[Residual] = []
    framework_origins = {"ECC", "DCC", "CCC", "CSCC", "OTCC", "TCC"}

    if reality_candidate.reality_candidate_id.upper() in framework_origins:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.REALITY_CANDIDATE,
                code="framework_origin_not_reality_origin",
                description="Framework identifiers cannot be used as reality candidates.",
            )
        )

    if not trace_candidates:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.TRACE_CANDIDATE,
                code="missing_trace_candidates",
                description="No trace candidates were provided.",
            )
        )

    if claim_candidate.domain_contract_id != domain_contract.domain_contract_id:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.CLAIM_CANDIDATE,
                code="claim_domain_mismatch",
                description="Claim candidate domain does not match domain contract.",
            )
        )

    if claim_candidate.defined_locus_id != defined_locus.defined_locus_id:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.CLAIM_CANDIDATE,
                code="claim_locus_mismatch",
                description="Claim candidate locus does not match defined locus.",
            )
        )

    if not evidence_bindings:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.EVIDENCE_BINDING,
                code="missing_evidence_bindings",
                description="No evidence bindings were provided.",
            )
        )

    trace_ids = {trace.trace_id for trace in trace_candidates}
    for binding in evidence_bindings:
        if binding.claim_id != claim_candidate.claim_id:
            residuals.append(
                Residual(
                    failed_stage=KnowledgeStage.EVIDENCE_BINDING,
                    code="binding_claim_mismatch",
                    description="Evidence binding points to another claim.",
                )
            )
        if binding.domain_contract_id != domain_contract.domain_contract_id:
            residuals.append(
                Residual(
                    failed_stage=KnowledgeStage.EVIDENCE_BINDING,
                    code="binding_domain_mismatch",
                    description="Evidence binding domain does not match domain contract.",
                )
            )
        if binding.defined_locus_id != defined_locus.defined_locus_id:
            residuals.append(
                Residual(
                    failed_stage=KnowledgeStage.EVIDENCE_BINDING,
                    code="binding_locus_mismatch",
                    description="Evidence binding locus does not match defined locus.",
                )
            )
        if any(trace_id not in trace_ids for trace_id in binding.trace_ids):
            residuals.append(
                Residual(
                    failed_stage=KnowledgeStage.EVIDENCE_BINDING,
                    code="binding_trace_missing",
                    description="Evidence binding includes unknown trace ids.",
                )
            )

    rank_ceiling = KnowledgeRank.ASSURED
    if evidence_bindings:
        binding_ceilings: list[KnowledgeRank] = []
        trace_index = {trace.trace_id: trace for trace in trace_candidates}
        for binding in evidence_bindings:
            ceiling = binding_rank_ceiling(binding)
            bound_traces = [trace_index[trace_id] for trace_id in binding.trace_ids if trace_id in trace_index]
            if bound_traces and all(trace.trace_type == "metric" for trace in bound_traces):
                ceiling = min(ceiling, KnowledgeRank.CANDIDATE)
            binding_ceilings.append(ceiling)
        rank_ceiling = min(binding_ceilings)

    final_rank = min(requested_rank, rank_ceiling)
    blocking = tuple(residual for residual in residuals if residual.blocking)
    status = JudgmentStatus.SUPPORTED if not blocking else JudgmentStatus.BLOCKED
    failed_stage = blocking[0].failed_stage if blocking else None

    judgment = JudgmentCandidate(
        judgment_type="KNOWLEDGE_TRANSITION",
        judgment_status=status,
        rank=final_rank if not blocking else KnowledgeRank.CANDIDATE,
        failed_stage=failed_stage,
        residuals=tuple(residuals),
    )

    transition_trace = (
        KnowledgeStage.REALITY_CANDIDATE,
        KnowledgeStage.TRACE_CANDIDATE,
        KnowledgeStage.DEFINED_LOCUS,
        KnowledgeStage.DOMAIN_CONTRACT,
        KnowledgeStage.CLAIM_CANDIDATE,
        KnowledgeStage.RELATION_CANDIDATE,
        KnowledgeStage.EVIDENCE_BINDING,
        KnowledgeStage.RANK_ASSIGNMENT,
        KnowledgeStage.RESIDUAL_AUDIT,
        KnowledgeStage.JUDGMENT_CANDIDATE,
    )

    return ApprovedKnowledgeContext(
        knowledge_context_id=knowledge_context_id,
        reality_candidate=reality_candidate,
        trace_candidates=trace_candidates,
        defined_locus=defined_locus,
        domain_contract=domain_contract,
        claim_candidate=claim_candidate,
        relation_candidates=relation_candidates,
        evidence_bindings=evidence_bindings,
        rank=judgment.rank,
        rank_ceiling=rank_ceiling,
        failed_stage=failed_stage,
        residuals=tuple(residuals),
        judgment_candidate=judgment,
        approved=not blocking,
        transition_trace=transition_trace,
    )
