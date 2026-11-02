"""The §9 decision envelope: every required key is present, and a missing action stage is visible as None."""

import pytest

from knowledge_constitution import (
    REQUIRED_ENVELOPE_KEYS,
    ClaimCandidate,
    DefinedLocus,
    DomainContract,
    EvidenceBinding,
    KnowledgeRank,
    RealityCandidate,
    RelationCandidate,
    TraceCandidate,
    decision_envelope,
    evaluate_action_license,
    evaluate_knowledge_transition,
)

# the list in docs/00_KNOWLEDGE_CONSTITUTION.md §9, copied by hand so the test does not mirror the code
CONSTITUTION_SECTION_9 = (
    "knowledge_context_id", "reality_candidate_id", "trace_ids", "defined_locus_id", "domain_contract_id",
    "claim_id", "relation_ids", "normative_source_ids", "applicability_result", "evidence_binding_ids",
    "rank", "rank_ceiling", "failed_stage", "residuals", "judgment_type", "judgment_status",
    "action_license", "handoff", "transition_trace", "feedback_requirement",
)


def _context(requested_rank=KnowledgeRank.SUPPORTED):
    return evaluate_knowledge_transition(
        knowledge_context_id="kc-env",
        reality_candidate=RealityCandidate("asset-1", "SYSTEM", "2026-Q3", "inventory", ("asset_tag",)),
        trace_candidates=(TraceCandidate("trace-1", "asset-1", "repo://evidence", "org/it", "owner-1", "2026-08-01", "DCC-01"),),
        defined_locus=DefinedLocus("locus-1", "BUSINESS_UNIT", "asset-1", "it-dept", "2026-Q3"),
        domain_contract=DomainContract("domain-1", "grc-v1", ("supports",), ("provenance_required",), "default"),
        claim_candidate=ClaimCandidate("claim-1", "locus-1", "control DCC-01 exists", "supports", "2026-Q3", "domain-1", "documentary"),
        relation_candidates=(RelationCandidate("rel-1", "locus-1", "claim-1", "supports", "domain-1", ("trace-1",)),),
        evidence_bindings=(EvidenceBinding("binding-1", "claim-1", "locus-1", "domain-1", ("trace-1",)),),
        requested_rank=requested_rank,
    )


def test_required_keys_match_constitution_section_9() -> None:
    assert set(REQUIRED_ENVELOPE_KEYS) == set(CONSTITUTION_SECTION_9)
    envelope = decision_envelope(_context())
    assert set(envelope) == set(CONSTITUTION_SECTION_9)


def test_missing_action_stage_is_visible_not_implied() -> None:
    envelope = decision_envelope(_context())
    assert envelope["action_license"] is None
    assert envelope["handoff"] is None
    assert envelope["feedback_requirement"] is None
    assert envelope["judgment_status"] == "SUPPORTED"
    assert envelope["rank"] == "SUPPORTED"


def test_action_stage_is_projected_without_recomputing_judgment() -> None:
    context = _context()
    action = evaluate_action_license(context=context, action_license_id="al-env", action_type="open_followup_task")
    envelope = decision_envelope(context, action, normative_source_ids=("ECC",), applicability_result="branch_in_scope")
    assert envelope["action_license"]["granted"] is False
    assert envelope["handoff"]["route"] == "DEFERRAL_QUEUE"
    assert envelope["failed_stage"] == "ACTION_LICENSE"
    assert envelope["judgment_status"] == "SUPPORTED"  # the judgment is untouched by the action outcome
    assert envelope["transition_trace"][-1] == "HANDOFF"
    assert any(res["code"] == "rank_below_action_threshold" for res in envelope["residuals"])


def test_envelope_rejects_action_from_another_context() -> None:
    # blocked example: an action decision cannot be attached to a context it was not derived from
    context = _context()
    other = evaluate_action_license(context=_context(), action_license_id="al-x", action_type="t")
    foreign = type(other)(**{**other.__dict__, "knowledge_context_id": "kc-other"})
    with pytest.raises(ValueError):
        decision_envelope(context, foreign)
