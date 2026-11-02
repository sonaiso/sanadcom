"""Gates added to the kernel transition: identity, boundaries, relation anchoring and trace integrity.

Each test is a blocked example for one no-jump law in docs/00_KNOWLEDGE_CONSTITUTION.md.
"""

from knowledge_constitution import (
    ClaimCandidate,
    DefinedLocus,
    DomainContract,
    EvidenceBinding,
    KnowledgeRank,
    KnowledgeStage,
    RealityCandidate,
    RelationCandidate,
    TraceCandidate,
    evaluate_knowledge_transition,
)

_REALITY = RealityCandidate("asset-1", "SYSTEM", "2026-Q3", "inventory", ("asset_tag",))
_TRACE = TraceCandidate("trace-1", "asset-1", "repo://evidence", "org/it", "owner-1", "2026-08-01", "DCC-01")
_LOCUS = DefinedLocus("locus-1", "BUSINESS_UNIT", "asset-1", "it-dept", "2026-Q3")
_DOMAIN = DomainContract("domain-1", "grc-v1", ("supports",), ("provenance_required",), "default")
_CLAIM = ClaimCandidate("claim-1", "locus-1", "control DCC-01 exists", "supports", "2026-Q3", "domain-1", "documentary")
_RELATION = RelationCandidate("rel-1", "locus-1", "claim-1", "supports", "domain-1", ("trace-1",))
_BINDING = EvidenceBinding("binding-1", "claim-1", "locus-1", "domain-1", ("trace-1",))


def _run(**overrides):
    kwargs = dict(
        knowledge_context_id="kc-gates",
        reality_candidate=_REALITY,
        trace_candidates=(_TRACE,),
        defined_locus=_LOCUS,
        domain_contract=_DOMAIN,
        claim_candidate=_CLAIM,
        relation_candidates=(_RELATION,),
        evidence_bindings=(_BINDING,),
        requested_rank=KnowledgeRank.SUPPORTED,
    )
    kwargs.update(overrides)
    return evaluate_knowledge_transition(**kwargs)


def _codes(context) -> set[str]:
    return {res.code for res in context.residuals}


def test_baseline_passes_all_new_gates() -> None:
    context = _run()
    assert context.approved is True and context.residuals == ()


def test_identity_must_be_preserved_before_any_transition() -> None:
    # blocked example: unresolved identity residuals on the reality candidate
    reality = RealityCandidate("asset-1", "SYSTEM", "2026-Q3", "inventory", unresolved_identity_residuals=("two_asset_tags",))
    context = _run(reality_candidate=reality)
    assert context.approved is False
    assert context.failed_stage == KnowledgeStage.REALITY_CANDIDATE
    assert "unresolved_identity_residuals" in _codes(context)


def test_trace_must_observe_the_same_reality() -> None:
    # blocked example: a trace about another asset cannot support this candidate
    foreign = TraceCandidate("trace-1", "asset-2", "repo://evidence", "org/it", "owner-1", "2026-08-01", "DCC-01")
    context = _run(trace_candidates=(foreign,))
    assert context.failed_stage == KnowledgeStage.TRACE_CANDIDATE
    assert "trace_reality_mismatch" in _codes(context)


def test_no_judgment_before_locus_boundaries_are_established() -> None:
    # blocked example: boundary residuals on the locus
    locus = DefinedLocus("locus-1", "BUSINESS_UNIT", "asset-1", "it-dept", "2026-Q3", boundary_residuals=("shared_vlan",))
    context = _run(defined_locus=locus)
    assert context.failed_stage == KnowledgeStage.DEFINED_LOCUS
    assert "unresolved_boundary_residuals" in _codes(context)


def test_locus_must_belong_to_the_reality_candidate() -> None:
    locus = DefinedLocus("locus-1", "BUSINESS_UNIT", "asset-2", "it-dept", "2026-Q3")
    context = _run(defined_locus=locus)
    assert "locus_reality_mismatch" in _codes(context)
    assert context.failed_stage == KnowledgeStage.DEFINED_LOCUS


def test_no_claim_may_be_judged_without_relation_to_the_locus() -> None:
    # blocked example: no relation candidates at all
    context = _run(relation_candidates=())
    assert context.failed_stage == KnowledgeStage.RELATION_CANDIDATE
    assert "missing_relation_candidates" in _codes(context)


def test_relation_must_be_anchored_to_locus_or_claim() -> None:
    stray = RelationCandidate("rel-x", "other-a", "other-b", "supports", "domain-1", ("trace-1",))
    context = _run(relation_candidates=(stray,))
    assert "relation_unanchored" in _codes(context)
    assert context.approved is False


def test_relation_type_must_be_admissible_in_domain_contract() -> None:
    # blocked example: "implies" is not an admissible relation under grc-v1
    rel = RelationCandidate("rel-1", "locus-1", "claim-1", "implies", "domain-1", ("trace-1",))
    context = _run(relation_candidates=(rel,))
    assert "relation_type_not_admissible" in _codes(context)
    claim = ClaimCandidate("claim-1", "locus-1", "control DCC-01 exists", "implies", "2026-Q3", "domain-1", "documentary")
    context2 = _run(claim_candidate=claim)
    assert "claim_relation_not_admissible" in _codes(context2)
    assert context2.failed_stage == KnowledgeStage.CLAIM_CANDIDATE


def test_relation_citing_unknown_trace_is_blocked() -> None:
    rel = RelationCandidate("rel-1", "locus-1", "claim-1", "supports", "domain-1", ("ghost-trace",))
    context = _run(relation_candidates=(rel,))
    assert "relation_trace_missing" in _codes(context)


def test_trace_with_broken_provenance_caps_rank_at_candidate() -> None:
    # No rank may exceed the weakest evidence binding: a tampered trace drags the ceiling down even if the binding looks fine
    tampered = TraceCandidate("trace-1", "asset-1", "repo://evidence", "org/it", "owner-1", "2026-08-01", "DCC-01", integrity_ok=False)
    context = _run(trace_candidates=(tampered,), requested_rank=KnowledgeRank.ASSURED)
    assert context.rank_ceiling == KnowledgeRank.CANDIDATE
    assert context.rank == KnowledgeRank.CANDIDATE


def test_first_blocking_residual_names_the_earliest_failed_stage() -> None:
    # several gates fail at once; failed_stage must point at the earliest stage, not the last one checked
    reality = RealityCandidate("asset-1", "SYSTEM", "2026-Q3", "inventory", unresolved_identity_residuals=("dup",))
    context = _run(reality_candidate=reality, relation_candidates=())
    assert context.failed_stage == KnowledgeStage.REALITY_CANDIDATE
    assert {"unresolved_identity_residuals", "missing_relation_candidates"} <= _codes(context)
