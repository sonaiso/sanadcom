from knowledge_constitution import (
    ClaimCandidate,
    DefinedLocus,
    DomainContract,
    EvidenceBinding,
    JudgmentStatus,
    KnowledgeRank,
    KnowledgeStage,
    RealityCandidate,
    RelationCandidate,
    TraceCandidate,
    evaluate_knowledge_transition,
)


def _reality() -> RealityCandidate:
    return RealityCandidate(
        reality_candidate_id="asset-1",
        reality_type="SYSTEM",
        temporal_bounds="2026-Q3",
        observation_source="inventory",
        identity_conditions=("asset_tag",),
    )


def _trace(trace_id: str = "trace-1") -> TraceCandidate:
    return TraceCandidate(
        trace_id=trace_id,
        reality_candidate_id="asset-1",
        source="repo://evidence",
        scope="org/it",
        owner="owner-1",
        freshness="2026-08-01",
        control_binding="DCC-01",
    )


def _locus() -> DefinedLocus:
    return DefinedLocus(
        defined_locus_id="locus-1",
        locus_type="BUSINESS_UNIT",
        reality_candidate_id="asset-1",
        boundaries="it-dept",
        applicable_time="2026-Q3",
    )


def _domain() -> DomainContract:
    return DomainContract(
        domain_contract_id="domain-1",
        governing_vocabulary="grc-v1",
        admissible_relation_types=("supports",),
        evidence_rules=("provenance_required",),
        rank_policy="default",
    )


def _claim() -> ClaimCandidate:
    return ClaimCandidate(
        claim_id="claim-1",
        defined_locus_id="locus-1",
        predicate="control DCC-01 exists",
        relation_type="supports",
        temporal_scope="2026-Q3",
        domain_contract_id="domain-1",
        required_evidence_class="documentary",
    )


def _relation() -> RelationCandidate:
    return RelationCandidate(
        relation_id="rel-1",
        source_object_id="locus-1",
        target_object_id="claim-1",
        relation_type="supports",
        domain_contract_id="domain-1",
        evidence_trace_ids=("trace-1",),
    )


def _binding() -> EvidenceBinding:
    return EvidenceBinding(
        evidence_binding_id="binding-1",
        claim_id="claim-1",
        defined_locus_id="locus-1",
        domain_contract_id="domain-1",
        trace_ids=("trace-1",),
    )


def test_kernel_allows_licensed_successful_transition() -> None:
    context = evaluate_knowledge_transition(
        knowledge_context_id="kc-1",
        reality_candidate=_reality(),
        trace_candidates=(_trace(),),
        defined_locus=_locus(),
        domain_contract=_domain(),
        claim_candidate=_claim(),
        relation_candidates=(_relation(),),
        evidence_bindings=(_binding(),),
        requested_rank=KnowledgeRank.SUPPORTED,
    )

    assert context.approved is True
    assert context.judgment_candidate.judgment_status == JudgmentStatus.SUPPORTED
    assert context.failed_stage is None
    assert context.rank == KnowledgeRank.SUPPORTED


def test_kernel_blocks_failed_transition_and_records_residuals() -> None:
    bad_binding = EvidenceBinding(
        evidence_binding_id="binding-1",
        claim_id="claim-1",
        defined_locus_id="locus-1",
        domain_contract_id="domain-1",
        trace_ids=("missing-trace",),
    )

    context = evaluate_knowledge_transition(
        knowledge_context_id="kc-2",
        reality_candidate=_reality(),
        trace_candidates=(_trace(),),
        defined_locus=_locus(),
        domain_contract=_domain(),
        claim_candidate=_claim(),
        relation_candidates=(_relation(),),
        evidence_bindings=(bad_binding,),
        requested_rank=KnowledgeRank.VERIFIED,
    )

    assert context.approved is False
    assert context.failed_stage == KnowledgeStage.EVIDENCE_BINDING
    assert context.judgment_candidate.judgment_status == JudgmentStatus.BLOCKED
    assert any(res.code == "binding_trace_missing" for res in context.residuals)


def test_no_claim_without_domain_is_blocked() -> None:
    bad_claim = ClaimCandidate(
        claim_id="claim-1",
        defined_locus_id="locus-1",
        predicate="control DCC-01 exists",
        relation_type="supports",
        temporal_scope="2026-Q3",
        domain_contract_id="another-domain",
        required_evidence_class="documentary",
    )

    context = evaluate_knowledge_transition(
        knowledge_context_id="kc-3",
        reality_candidate=_reality(),
        trace_candidates=(_trace(),),
        defined_locus=_locus(),
        domain_contract=_domain(),
        claim_candidate=bad_claim,
        relation_candidates=(_relation(),),
        evidence_bindings=(_binding(),),
    )

    assert context.approved is False
    assert context.failed_stage == KnowledgeStage.CLAIM_CANDIDATE


def test_rank_cannot_exceed_weakest_binding_ceiling() -> None:
    weak_binding = EvidenceBinding(
        evidence_binding_id="binding-weak",
        claim_id="claim-1",
        defined_locus_id="locus-1",
        domain_contract_id="domain-1",
        trace_ids=("trace-1",),
        provenance_ok=False,
    )

    context = evaluate_knowledge_transition(
        knowledge_context_id="kc-4",
        reality_candidate=_reality(),
        trace_candidates=(_trace(),),
        defined_locus=_locus(),
        domain_contract=_domain(),
        claim_candidate=_claim(),
        relation_candidates=(_relation(),),
        evidence_bindings=(weak_binding,),
        requested_rank=KnowledgeRank.ASSURED,
    )

    assert context.rank_ceiling == KnowledgeRank.CANDIDATE
    assert context.rank == KnowledgeRank.CANDIDATE


def test_no_framework_origin_as_reality_origin() -> None:
    context = evaluate_knowledge_transition(
        knowledge_context_id="kc-5",
        reality_candidate=RealityCandidate("ECC", "SYSTEM", "2026-Q3", "inventory"),
        trace_candidates=(_trace(),),
        defined_locus=_locus(),
        domain_contract=_domain(),
        claim_candidate=_claim(),
        relation_candidates=(_relation(),),
        evidence_bindings=(_binding(),),
    )

    assert context.approved is False
    assert context.failed_stage == KnowledgeStage.REALITY_CANDIDATE
    assert any(res.code == "framework_origin_not_reality_origin" for res in context.residuals)


def test_metric_remains_trace_candidate_under_rank_ceiling() -> None:
    context = evaluate_knowledge_transition(
        knowledge_context_id="kc-6",
        reality_candidate=_reality(),
        trace_candidates=(
            TraceCandidate(
                trace_id="trace-1",
                reality_candidate_id="asset-1",
                source="repo://metric",
                scope="org/it",
                owner="owner-1",
                freshness="2026-08-01",
                control_binding="DCC-01",
                trace_type="metric",
            ),
        ),
        defined_locus=_locus(),
        domain_contract=_domain(),
        claim_candidate=_claim(),
        relation_candidates=(_relation(),),
        evidence_bindings=(_binding(),),
        requested_rank=KnowledgeRank.VERIFIED,
    )

    assert context.rank_ceiling == KnowledgeRank.CANDIDATE
    assert context.rank == KnowledgeRank.CANDIDATE
