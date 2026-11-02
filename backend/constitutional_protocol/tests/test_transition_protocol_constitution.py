import pytest

from constitutional_protocol import (
    ClosureBundle,
    ConstitutionalRank,
    DomainContract,
    EngineType,
    IdentityCertificate,
    ProtocolStage,
    RelationCertificate,
    RelationProposal,
    RelationType,
    Residual,
    ResidualKind,
    ScopeCertificate,
    ScopeProfile,
    TransitionProposal,
    TransitionStatus,
    UnitCertificate,
    evaluate_transition_proposal,
)


def _proposal() -> TransitionProposal:
    return TransitionProposal(
        proposal_id="proposal-1",
        proposer_type=EngineType.CAUSAL_ENGINE,
        source_refs=("event-A",),
        target_candidate_ref="event-B",
        proposed_relation=RelationProposal(
            relation_type=RelationType.TEMPORAL,
            source_refs=("event-A",),
            target_ref="event-B",
        ),
        domain_ref="causal-domain",
        scope_ref="org-q3",
        constitutive_evidence_refs=("trace-1",),
        supporting_evidence_refs=("trace-2",),
        proposed_rank=ConstitutionalRank.VERIFIED,
        trace_id="trace-1",
    )


def _unit() -> UnitCertificate:
    return UnitCertificate(
        certificate_id="unit-1",
        carrier_ref="event-A",
        boundary_rule="bounded_observation_window",
        unit_criterion="event_instance",
        source_trace_refs=("trace-1",),
    )


def _identity(*, basis: str = "trace_linked_identity") -> IdentityCertificate:
    return IdentityCertificate(
        certificate_id="identity-1",
        source_ref="event-A",
        target_ref="event-B",
        preserved=True,
        basis=basis,
        evidence_refs=("trace-1",),
    )


def _domain() -> DomainContract:
    return DomainContract(
        domain_id="causal-domain",
        unit_types=("event",),
        identity_policy_ref="id-policy-v1",
        allowed_relation_types=(RelationType.TEMPORAL, RelationType.CAUSAL),
        allowed_operation_types=("compare", "infer"),
        evidence_policy_ref="evidence-policy-v1",
        scope_policy_ref="scope-policy-v1",
        rank_policy_ref="rank-policy-v1",
    )


def _relation(*, relation_type: RelationType = RelationType.TEMPORAL) -> RelationCertificate:
    return RelationCertificate(
        certificate_id="relation-1",
        relation_type=relation_type,
        arity=2,
        direction="forward",
        source_roles=("source",),
        target_roles=("target",),
        preconditions=("ordered_events",),
        blockers=(),
        evidence_refs=("trace-1",),
    )


def _scope(*, license: bool = False) -> ScopeCertificate:
    return ScopeCertificate(
        certificate_id="scope-1",
        supported_scope=ScopeProfile(temporal="Q3-2026", quantifier="sample"),
        certified_scope=ScopeProfile(temporal="Q3-2026", quantifier="sample"),
        generalization_license=license,
    )


def _closure(*, all_true: bool = True) -> ClosureBundle:
    return ClosureBundle(
        structural=all_true,
        referential=all_true,
        inferential=all_true,
        epistemic=all_true,
    )


def test_fully_licensed_transition_is_certified() -> None:
    decision = evaluate_transition_proposal(
        proposal=_proposal(),
        certifier_authority="INDEPENDENT_REVIEW_BOARD",
        unit_certificate=_unit(),
        identity_certificate=_identity(),
        domain_contract=_domain(),
        relation_certificate=_relation(),
        scope_certificate=_scope(),
        closure_bundle=_closure(),
    )

    assert decision.status == TransitionStatus.CERTIFIED
    assert decision.transition_certificate is not None
    assert decision.certified_rank == ConstitutionalRank.VERIFIED


def test_self_certification_is_blocked() -> None:
    decision = evaluate_transition_proposal(
        proposal=_proposal(),
        certifier_authority="CAUSAL_ENGINE",
        unit_certificate=_unit(),
        identity_certificate=_identity(),
        domain_contract=_domain(),
        relation_certificate=_relation(),
        scope_certificate=_scope(),
        closure_bundle=_closure(),
    )

    assert decision.status == TransitionStatus.BLOCKED
    assert any(res.kind == ResidualKind.SELF_CERTIFICATION for res in decision.residuals)


def test_no_certificate_without_ancestry_is_blocked() -> None:
    decision = evaluate_transition_proposal(
        proposal=_proposal(),
        certifier_authority="INDEPENDENT_REVIEW_BOARD",
        unit_certificate=_unit(),
        identity_certificate=_identity(),
        domain_contract=_domain(),
        relation_certificate=None,
        scope_certificate=_scope(),
        closure_bundle=_closure(),
    )

    assert decision.status == TransitionStatus.BLOCKED
    assert decision.failed_stage == ProtocolStage.RELATION
    assert any(res.code == "missing_relation_certificate" for res in decision.residuals)


def test_no_identity_from_similarity() -> None:
    decision = evaluate_transition_proposal(
        proposal=_proposal(),
        certifier_authority="INDEPENDENT_REVIEW_BOARD",
        unit_certificate=_unit(),
        identity_certificate=_identity(basis="similarity"),
        domain_contract=_domain(),
        relation_certificate=_relation(),
        scope_certificate=_scope(),
        closure_bundle=_closure(),
    )

    assert decision.status == TransitionStatus.BLOCKED
    assert any(res.code == "identity_from_similarity_forbidden" for res in decision.residuals)


def test_no_relation_type_upgrade_temporal_to_causal() -> None:
    decision = evaluate_transition_proposal(
        proposal=_proposal(),
        certifier_authority="INDEPENDENT_REVIEW_BOARD",
        unit_certificate=_unit(),
        identity_certificate=_identity(),
        domain_contract=_domain(),
        relation_certificate=_relation(relation_type=RelationType.CAUSAL),
        scope_certificate=_scope(),
        closure_bundle=_closure(),
    )

    assert decision.status == TransitionStatus.BLOCKED
    assert any(res.code == "relation_type_upgrade_forbidden" for res in decision.residuals)


def test_no_scope_expansion_without_license() -> None:
    scope_certificate = ScopeCertificate(
        certificate_id="scope-1",
        supported_scope=ScopeProfile(temporal="Q3-2026", quantifier="sample"),
        certified_scope=ScopeProfile(temporal="Q3-2026", quantifier="all"),
        generalization_license=False,
    )
    decision = evaluate_transition_proposal(
        proposal=_proposal(),
        certifier_authority="INDEPENDENT_REVIEW_BOARD",
        unit_certificate=_unit(),
        identity_certificate=_identity(),
        domain_contract=_domain(),
        relation_certificate=_relation(),
        scope_certificate=scope_certificate,
        closure_bundle=_closure(),
    )

    assert decision.status == TransitionStatus.BLOCKED
    assert any(res.code == "scope_expansion_without_license" for res in decision.residuals)


def test_rank_cannot_exceed_weakest_ceiling() -> None:
    warning = Residual(
        code="trace_quality_warning",
        kind=ResidualKind.ALTERNATIVE_UNCHECKED,
        stage=ProtocolStage.CLOSURE,
        description="Alternative explanation has not been evaluated yet.",
        blocking=False,
        rank_ceiling=ConstitutionalRank.PLAUSIBLE,
        trace_ref="trace-1",
        reopen_condition="Evaluate alternative branch and submit result.",
    )
    decision = evaluate_transition_proposal(
        proposal=_proposal(),
        certifier_authority="INDEPENDENT_REVIEW_BOARD",
        unit_certificate=_unit(),
        identity_certificate=_identity(),
        domain_contract=_domain(),
        relation_certificate=_relation(),
        scope_certificate=_scope(),
        closure_bundle=_closure(),
        existing_residuals=(warning,),
    )

    assert decision.status == TransitionStatus.SUSPENDED
    assert decision.rank_ceiling == ConstitutionalRank.PLAUSIBLE
    assert decision.certified_rank == ConstitutionalRank.PLAUSIBLE


def test_no_closure_with_blocking_residual() -> None:
    decision = evaluate_transition_proposal(
        proposal=_proposal(),
        certifier_authority="INDEPENDENT_REVIEW_BOARD",
        unit_certificate=_unit(),
        identity_certificate=_identity(),
        domain_contract=_domain(),
        relation_certificate=_relation(),
        scope_certificate=_scope(),
        closure_bundle=_closure(all_true=False),
    )

    assert decision.status == TransitionStatus.BLOCKED
    assert any(res.code == "closure_bundle_incomplete" for res in decision.residuals)


def test_every_certificate_requires_reopen_conditions() -> None:
    with pytest.raises(ValueError, match="reopen_conditions are required"):
        from constitutional_protocol.contracts import TransitionCertificate

        TransitionCertificate(
            proposal_id="proposal-1",
            unit_certificate_id="unit-1",
            identity_certificate_id="identity-1",
            domain_id="domain-1",
            relation_certificate_id="relation-1",
            scope_certificate_id="scope-1",
            closure_bundle=_closure(),
            residual_ids=(),
            certified_rank=ConstitutionalRank.SUPPORTED,
            decision=TransitionStatus.CERTIFIED,
            constitution_version="1.0.0",
            trace_id="trace-1",
            reopen_conditions=(),
        )
