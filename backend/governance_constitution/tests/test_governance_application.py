from dataclasses import replace

import pytest

from governance_constitution.application import evaluate_governance_application
from governance_constitution.contracts import BranchLicense, Condition, GovernanceApplicabilityBinding, Mani, RankPolicy
from governance_constitution.enums import DecisionStatus, EvidenceRank
from knowledge_constitution import (
    ApprovedKnowledgeContext,
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


def _license(
    *,
    conditions: tuple[Condition | str, ...] = (Condition("data_inventory"),),
    mani: tuple[Mani | str, ...] = (),
    minimum_action_rank: EvidenceRank = EvidenceRank.SUPPORTED,
) -> BranchLicense:
    return BranchLicense(
        origin="ECC",
        branch_id="DCC",
        effective_attribute="data lifecycle",
        sabab="organizational data assets",
        conditions=conditions,
        mani=mani,
        qadih_differences=(),
        evidence_requirements=("source", "scope", "owner", "freshness", "control_binding"),
        rank_policy=RankPolicy(minimum_action_rank=minimum_action_rank),
        residual_policy="record_all_failures",
    )


def _approved_context(*, relation_type: str = "supports", requested_rank: KnowledgeRank = KnowledgeRank.SUPPORTED) -> tuple[ApprovedKnowledgeContext, EvidenceBinding]:
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
            relation_type,
            "2026-Q3",
            "domain-1",
            "documentary",
        ),
        relation_candidates=(
            RelationCandidate("rel-1", "locus-1", "claim-1", relation_type, "domain-1", ("trace-1",)),
        ),
        evidence_bindings=(binding,),
        requested_rank=requested_rank,
    )
    return context, binding


def _binding(context: ApprovedKnowledgeContext, binding: EvidenceBinding, **overrides: object) -> GovernanceApplicabilityBinding:
    payload = {
        "binding_id": "ga-1",
        "knowledge_context_id": context.knowledge_context_id,
        "normative_source_id": "ECC",
        "branch_id": "DCC",
        "defined_locus_id": context.defined_locus.defined_locus_id,
        "domain_contract_id": context.domain_contract.domain_contract_id,
        "applicability_claim_id": context.claim_candidate.claim_id,
        "effective_attribute_claim_id": context.claim_candidate.claim_id,
        "sabab_claim_id": context.claim_candidate.claim_id,
        "condition_claim_ids": (context.claim_candidate.claim_id,),
        "blocker_claim_ids": (),
        "evidence_binding_ids": (binding.evidence_binding_id,),
    }
    payload.update(overrides)
    return GovernanceApplicabilityBinding(**payload)


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
            applicability_binding=_binding(context, binding),
            evidence_binding_ids=(binding.evidence_binding_id,),
        )


def test_condition_is_not_satisfied_merely_because_license_declares_it() -> None:
    context, binding = _approved_context()
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=()),
        applicability_binding=_binding(context, binding),
        evidence_binding_ids=(binding.evidence_binding_id,),
    )
    assert result.constitutional_decision.conditions_evaluated[0].satisfied is None
    assert result.constitutional_decision.status == DecisionStatus.DEFERRED


def test_unknown_condition_defers_governance_judgment() -> None:
    context, binding = _approved_context()
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=()),
        applicability_binding=_binding(context, binding),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": None},
    )
    assert result.constitutional_decision.status == DecisionStatus.DEFERRED
    assert any(res.code == "unknown_condition_state" for res in result.constitutional_decision.residuals)


def test_unknown_mani_does_not_become_inactive() -> None:
    context, binding = _approved_context()
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=(Mani("missing-owner"),)),
        applicability_binding=_binding(context, binding),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
        mani_states={"missing-owner": None},
    )
    assert result.constitutional_decision.status == DecisionStatus.HUMAN_REVIEW_REQUIRED
    assert any(res.code == "unknown_mani_state" for res in result.constitutional_decision.residuals)


def test_missing_sabab_blocks_applicability_binding() -> None:
    context, binding = _approved_context()
    license_without_sabab = _license(conditions=(Condition("data_inventory"),), mani=())
    object.__setattr__(license_without_sabab, "sabab", None)
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=license_without_sabab,
        applicability_binding=_binding(context, binding),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
    )
    assert result.constitutional_decision.status != DecisionStatus.ALLOWED
    assert any(res.code == "applicability_sabab_not_proven" for res in result.constitutional_decision.residuals)


def test_mutated_binding_with_known_id_is_rejected() -> None:
    context, binding = _approved_context()
    mutated = EvidenceBinding(
        evidence_binding_id=binding.evidence_binding_id,
        claim_id="claim-other",
        defined_locus_id=binding.defined_locus_id,
        domain_contract_id=binding.domain_contract_id,
        trace_ids=binding.trace_ids,
    )
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=()),
        applicability_binding=_binding(context, binding),
        evidence_bindings=(mutated,),
        condition_states={"data_inventory": True},
    )
    assert any(res.code == "mutated_evidence_binding" for res in result.constitutional_decision.residuals)


def test_binding_claim_must_match_approved_context_claim() -> None:
    context, binding = _approved_context()
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=()),
        applicability_binding=_binding(context, binding, applicability_claim_id="claim-x"),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
    )
    assert any(res.code == "binding_claim_mismatch" for res in result.constitutional_decision.residuals)


def test_binding_locus_must_match_approved_context_locus() -> None:
    context, binding = _approved_context()
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=()),
        applicability_binding=_binding(context, binding, defined_locus_id="locus-x"),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
    )
    assert any(res.code == "binding_locus_mismatch" for res in result.constitutional_decision.residuals)


def test_binding_domain_must_match_approved_context_domain() -> None:
    context, binding = _approved_context()
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=()),
        applicability_binding=_binding(context, binding, domain_contract_id="domain-x"),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
    )
    assert any(res.code == "binding_domain_mismatch" for res in result.constitutional_decision.residuals)


def test_knowledge_claim_type_must_support_governance_judgment_type() -> None:
    context, binding = _approved_context(relation_type="describes")
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=()),
        applicability_binding=_binding(context, binding),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
    )
    assert any(res.code == "claim_relation_not_applicable" for res in result.constitutional_decision.residuals)


def test_minimum_action_rank_does_not_cap_knowledge_rank() -> None:
    context, binding = _approved_context()
    context = replace(context, rank=KnowledgeRank.VERIFIED, rank_ceiling=KnowledgeRank.VERIFIED)
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(minimum_action_rank=EvidenceRank.SUPPORTED),
        applicability_binding=_binding(context, binding),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
    )
    assert result.constitutional_decision.rank == EvidenceRank.VERIFIED


def test_verified_context_remains_verified_when_action_threshold_is_supported() -> None:
    context, binding = _approved_context()
    context = replace(context, rank=KnowledgeRank.VERIFIED, rank_ceiling=KnowledgeRank.VERIFIED)
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(minimum_action_rank=EvidenceRank.SUPPORTED),
        applicability_binding=_binding(context, binding),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
    )
    assert result.constitutional_decision.rank == EvidenceRank.VERIFIED


def test_governance_license_must_be_bound_to_normative_source() -> None:
    context, binding = _approved_context()
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=()),
        applicability_binding=_binding(context, binding, normative_source_id="ISO-27001"),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
    )
    assert any(res.code == "normative_source_mismatch" for res in result.constitutional_decision.residuals)


def test_foreign_branch_license_cannot_consume_approved_context() -> None:
    context, binding = _approved_context()
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=()),
        applicability_binding=_binding(context, binding, branch_id="CCC"),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
    )
    assert any(res.code == "foreign_branch_license_binding" for res in result.constitutional_decision.residuals)


def test_expected_governance_failure_returns_residual_not_raw_exception() -> None:
    context, binding = _approved_context()
    result = evaluate_governance_application(
        knowledge_context=context,
        applicability_license=_license(conditions=(Condition("data_inventory"),), mani=()),
        applicability_binding=_binding(context, binding, normative_source_id="ISO-27001"),
        evidence_binding_ids=(binding.evidence_binding_id,),
        condition_states={"data_inventory": True},
    )
    assert result.constitutional_decision.status in {
        DecisionStatus.DEFERRED,
        DecisionStatus.HUMAN_REVIEW_REQUIRED,
        DecisionStatus.CANDIDATE,
        DecisionStatus.BLOCKED,
    }
    assert result.constitutional_decision.residuals
