"""Constitutional tests for stages 11-14: judgment -> action licence -> handoff -> feedback -> reality re-evaluation.

Each test names the no-jump law it protects. Negative tests are blocked examples by design.
"""

import pytest

from knowledge_constitution import (
    ActionDecision,
    ClaimCandidate,
    DefinedLocus,
    DomainContract,
    EvidenceBinding,
    FeedbackTrace,
    HandoffRoute,
    KnowledgeRank,
    KnowledgeStage,
    RealityCandidate,
    RelationCandidate,
    TraceCandidate,
    evaluate_action_license,
    evaluate_knowledge_transition,
    record_feedback,
)


def _context(*, requested_rank=KnowledgeRank.VERIFIED, binding=None, reality_id="asset-1"):
    trace = TraceCandidate("trace-1", reality_id, "repo://evidence", "org/it", "owner-1", "2026-08-01", "DCC-01")
    binding = binding or EvidenceBinding("binding-1", "claim-1", "locus-1", "domain-1", ("trace-1",))
    return evaluate_knowledge_transition(
        knowledge_context_id="kc-action",
        reality_candidate=RealityCandidate(reality_id, "SYSTEM", "2026-Q3", "inventory", ("asset_tag",)),
        trace_candidates=(trace,),
        defined_locus=DefinedLocus("locus-1", "BUSINESS_UNIT", reality_id, "it-dept", "2026-Q3"),
        domain_contract=DomainContract("domain-1", "grc-v1", ("supports",), ("provenance_required",), "default"),
        claim_candidate=ClaimCandidate("claim-1", "locus-1", "control DCC-01 exists", "supports", "2026-Q3", "domain-1", "documentary"),
        relation_candidates=(RelationCandidate("rel-1", "locus-1", "claim-1", "supports", "domain-1", ("trace-1",)),),
        evidence_bindings=(binding,),
        requested_rank=requested_rank,
    )


def test_supported_judgment_with_sufficient_rank_is_licensed_and_routed_to_automation() -> None:
    context = _context(requested_rank=KnowledgeRank.SUPPORTED)
    decision = evaluate_action_license(
        context=context, action_license_id="al-1", action_type="open_followup_task", minimum_rank=KnowledgeRank.SUPPORTED
    )
    assert decision.action_license.granted is True
    assert decision.failed_stage is None
    assert decision.handoff.route == HandoffRoute.AUTOMATION
    assert decision.feedback_requirement.required is True
    assert decision.feedback_requirement.action_license_id == "al-1"
    assert decision.transition_trace[-2:] == (KnowledgeStage.ACTION_LICENSE, KnowledgeStage.HANDOFF)


def test_no_judgment_directly_becomes_an_action() -> None:
    # blocked example: a supported judgment below the action threshold is deferred, never executed
    context = _context(requested_rank=KnowledgeRank.SUPPORTED)
    assert context.approved is True
    decision = evaluate_action_license(context=context, action_license_id="al-2", action_type="close_finding")
    assert decision.action_license.granted is False
    assert decision.failed_stage == KnowledgeStage.ACTION_LICENSE
    assert any(res.code == "rank_below_action_threshold" for res in decision.residuals)
    assert decision.handoff.route == HandoffRoute.DEFERRAL_QUEUE
    assert decision.feedback_requirement.required is False


def test_rank_is_never_raised_to_permit_an_action() -> None:
    # blocked example: requesting VERIFIED does not lift a binding whose ceiling is SUPPORTED
    context = _context(requested_rank=KnowledgeRank.VERIFIED)
    assert context.rank == KnowledgeRank.SUPPORTED
    decision = evaluate_action_license(context=context, action_license_id="al-3", action_type="close_finding")
    assert decision.action_license.rank_at_licensing == KnowledgeRank.SUPPORTED
    assert decision.action_license.granted is False


def test_blocked_judgment_goes_to_human_review_with_residuals() -> None:
    # blocked example: a binding citing an unknown trace blocks the judgment and therefore the action
    bad = EvidenceBinding("binding-1", "claim-1", "locus-1", "domain-1", ("missing-trace",))
    context = _context(binding=bad)
    assert context.approved is False
    decision = evaluate_action_license(
        context=context, action_license_id="al-4", action_type="close_finding", minimum_rank=KnowledgeRank.CANDIDATE
    )
    assert decision.action_license.granted is False
    assert {res.code for res in decision.residuals} >= {"judgment_not_approved", "unresolved_blocking_residuals"}
    assert decision.handoff.route == HandoffRoute.HUMAN_REVIEW


def test_active_blocker_prevents_action_even_with_sufficient_rank() -> None:
    # blocked example: an active mani is a gate, not a note
    context = _context(requested_rank=KnowledgeRank.SUPPORTED)
    decision = evaluate_action_license(
        context=context,
        action_license_id="al-5",
        action_type="open_followup_task",
        minimum_rank=KnowledgeRank.SUPPORTED,
        active_blockers=("legal_hold",),
    )
    assert decision.action_license.granted is False
    assert any(res.code == "active_blocker:legal_hold" for res in decision.residuals)
    assert decision.handoff.route == HandoffRoute.HUMAN_REVIEW


def test_feedback_closes_the_loop_with_a_new_reality_candidate() -> None:
    context = _context(requested_rank=KnowledgeRank.SUPPORTED)
    decision = evaluate_action_license(
        context=context, action_license_id="al-6", action_type="open_followup_task", minimum_rank=KnowledgeRank.SUPPORTED
    )
    result = record_feedback(
        decision=decision,
        feedback=FeedbackTrace("fb-1", "al-6", "asset-1", "task opened in tracker #42", "2026-08-02", "tracker", True),
        reality_type="SYSTEM",
        identity_conditions=("asset_tag",),
    )
    assert result.accepted is True
    assert result.reality_reevaluation is not None
    assert result.reality_reevaluation.observation_source == "tracker"
    assert result.transition_trace[-1] == KnowledgeStage.REALITY_REEVALUATION


def test_no_action_is_complete_without_feedback_trace_bound_to_its_license() -> None:
    # blocked example: feedback that names another licence or another reality is rejected with residuals
    context = _context(requested_rank=KnowledgeRank.SUPPORTED)
    decision = evaluate_action_license(
        context=context, action_license_id="al-7", action_type="open_followup_task", minimum_rank=KnowledgeRank.SUPPORTED
    )
    result = record_feedback(
        decision=decision,
        feedback=FeedbackTrace("fb-2", "al-OTHER", "asset-9", "something happened", "2026-08-02", "tracker", True),
        reality_type="SYSTEM",
    )
    assert result.accepted is False
    assert result.failed_stage == KnowledgeStage.FEEDBACK_TRACE
    assert {res.code for res in result.residuals} == {"feedback_license_mismatch", "feedback_reality_mismatch"}


def test_feedback_for_ungranted_action_is_rejected() -> None:
    # blocked example: nothing was executed, so nothing can be fed back
    context = _context(requested_rank=KnowledgeRank.SUPPORTED)
    decision = evaluate_action_license(context=context, action_license_id="al-8", action_type="close_finding")
    assert decision.action_license.granted is False
    result = record_feedback(
        decision=decision,
        feedback=FeedbackTrace("fb-3", "al-8", "asset-1", "closed", "2026-08-02", "ui", True),
        reality_type="SYSTEM",
    )
    assert result.accepted is False
    assert any(res.code == "feedback_for_ungranted_action" for res in result.residuals)


def test_action_decision_shape_is_frozen() -> None:
    context = _context(requested_rank=KnowledgeRank.SUPPORTED)
    decision = evaluate_action_license(
        context=context, action_license_id="al-9", action_type="open_followup_task", minimum_rank=KnowledgeRank.SUPPORTED
    )
    assert isinstance(decision, ActionDecision)
    with pytest.raises(Exception):
        decision.action_license.granted = False  # type: ignore[misc]
