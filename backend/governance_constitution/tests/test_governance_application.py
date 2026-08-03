import pytest

from governance_constitution.application import evaluate_governance_application
from governance_constitution.contracts import BranchLicense, Condition, Mani, RankPolicy
from governance_constitution.enums import DecisionStatus, EvidenceRank
from knowledge_constitution import (
    ClaimCandidate,
    DefinedLocus,
    DomainContract,
    EvidenceBinding,
    KnowledgeRank,
    RealityCandidate,
    RelationCandidate,
    TraceCandidate,
    evaluate_knowledge_transition,
)


def _license() -> BranchLicense:
    return BranchLicense(
        origin="ECC",
        branch_id="DCC",
        effective_attribute="data lifecycle",
        sabab="organizational data assets",
        conditions=(Condition("data_inventory"),),
        mani=(Mani("none"),),
        qadih_differences=(),
        evidence_requirements=("source", "scope", "owner", "freshness", "control_binding"),
        rank_policy=RankPolicy(minimum_action_rank=EvidenceRank.SUPPORTED),
        residual_policy="record_all_failures",
    )


def _approved_context() -> tuple[object, EvidenceBinding]:
    binding = EvidenceBinding(
        evidence_binding_id="binding-1",
        claim_id="claim-1",
        defined_locus_id="locus-1",
        domain_contract_id="domain-1",
        trace_ids=("trace-1",),
    )
    context = evaluate_knowledge_transition(
        knowledge_context_id="kc-10",
        reality_candidate=RealityCandidate("asset-1", "SYSTEM", "2026-Q3", "inventory"),
        trace_candidates=(
            TraceCandidate(
                trace_id="trace-1",
                reality_candidate_id="asset-1",
                source="repo://evidence",
                scope="org/it",
                owner="owner-1",
                freshness="2026-08-01",
                control_binding="DCC-01",
            ),
        ),
        defined_locus=DefinedLocus("locus-1", "BUSINESS_UNIT", "asset-1", "it-dept", "2026-Q3"),
        domain_contract=DomainContract("domain-1", "grc-v1", ("supports",), ("provenance_required",), "default"),
        claim_candidate=ClaimCandidate(
            "claim-1",
            "locus-1",
            "control DCC-01 exists",
            "supports",
            "2026-Q3",
            "domain-1",
            "documentary",
        ),
        relation_candidates=(
            RelationCandidate("rel-1", "locus-1", "claim-1", "supports", "domain-1", ("trace-1",)),
        ),
        evidence_bindings=(binding,),
        requested_rank=KnowledgeRank.SUPPORTED,
    )
    return context, binding


def test_governance_requires_approved_knowledge_context() -> None:
    context, binding = _approved_context()
    blocked_context = evaluate_knowledge_transition(
        knowledge_context_id=context.knowledge_context_id,
        reality_candidate=context.reality_candidate,
        trace_candidates=context.trace_candidates,
        defined_locus=context.defined_locus,
        domain_contract=context.domain_contract,
        claim_candidate=context.claim_candidate,
        relation_candidates=context.relation_candidates,
        evidence_bindings=(),
    )
    with pytest.raises(ValueError, match="approved knowledge context"):
        evaluate_governance_application(
            knowledge_context=blocked_context,
            applicability_license=_license(),
            evidence_bindings=(binding,),
        )


def test_governance_application_uses_knowledge_context_and_returns_candidate() -> None:
    context, binding = _approved_context()
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(),
        evidence_bindings=(binding,),
    )

    assert result.knowledge_context_id == "kc-10"
    assert result.constitutional_decision.status in {DecisionStatus.ALLOWED, DecisionStatus.CANDIDATE}
    assert result.constitutional_decision.rank <= EvidenceRank.SUPPORTED
