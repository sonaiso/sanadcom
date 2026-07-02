from pathlib import Path

from governance_constitution.contracts import (
    BranchLicense,
    Decision,
    FailedStage,
    Rank,
    TransitionRequest,
)
from governance_constitution.guard import evaluate_transition


def _license() -> BranchLicense:
    return BranchLicense(
        origin="ECC",
        branch="DCC",
        effective_attribute="data lifecycle",
        sabab="organizational data assets",
        conditions=["data_inventory", "data_owner"],
        blockers=[],
        qadih_differences=[],
        evidence_requirements=["trace", "scope", "owner", "freshness", "control_binding"],
        rank_policy={"delivery": "VERIFIED"},
        residual_policy="record_all_failures",
    )


def _valid_request() -> TransitionRequest:
    return TransitionRequest(
        origin="ECC",
        branch="DCC",
        effective_attribute="data lifecycle",
        sabab="organizational data assets",
        provided_conditions=["data_inventory", "data_owner"],
        blockers=[],
        qadih_differences=[],
        evidence_trace={
            "trace": "ev-1",
            "scope": "org",
            "owner": "grc-owner",
            "freshness": "2026-01-01",
            "control_binding": "DCC-01",
        },
        requested_rank=Rank.VERIFIED,
        minimum_action_rank=Rank.VERIFIED,
        action_requested=True,
    )


def test_no_branch_without_origin_is_blocked() -> None:
    request = _valid_request()
    request = TransitionRequest(**{**request.__dict__, "origin": None})
    decision = evaluate_transition(request, _license())
    assert decision.decision == Decision.BLOCKED
    assert decision.failed_stage == FailedStage.ORIGIN


def test_no_branch_license_is_blocked() -> None:
    decision = evaluate_transition(_valid_request(), None)
    assert decision.decision == Decision.BLOCKED
    assert decision.failed_stage == FailedStage.BRANCH_LICENSE


def test_license_origin_branch_mismatch_is_blocked() -> None:
    bad_license = BranchLicense(**{**_license().__dict__, "branch": "CCC"})
    decision = evaluate_transition(_valid_request(), bad_license)
    assert decision.decision == Decision.BLOCKED
    assert decision.failed_stage == FailedStage.BRANCH_LICENSE


def test_missing_effective_attribute_is_blocked() -> None:
    request = TransitionRequest(**{**_valid_request().__dict__, "effective_attribute": None})
    decision = evaluate_transition(request, _license())
    assert decision.decision == Decision.BLOCKED
    assert decision.failed_stage == FailedStage.EFFECTIVE_ATTRIBUTE


def test_missing_sabab_is_blocked() -> None:
    request = TransitionRequest(**{**_valid_request().__dict__, "sabab": None})
    decision = evaluate_transition(request, _license())
    assert decision.decision == Decision.BLOCKED
    assert decision.failed_stage == FailedStage.SABAB


def test_missing_conditions_create_residuals() -> None:
    request = TransitionRequest(**{**_valid_request().__dict__, "provided_conditions": ["data_inventory"]})
    decision = evaluate_transition(request, _license())
    assert decision.decision == Decision.DEFERRED
    assert any(res.stage == FailedStage.CONDITION for res in decision.residuals)


def test_mani_blocks_transition() -> None:
    request = TransitionRequest(**{**_valid_request().__dict__, "blockers": ["missing_scope"]})
    decision = evaluate_transition(request, _license())
    assert decision.decision == Decision.BLOCKED
    assert any(res.stage == FailedStage.MANI for res in decision.residuals)


def test_qadih_difference_prevents_verified_rank() -> None:
    request = TransitionRequest(
        **{**_valid_request().__dict__, "qadih_differences": ["asset_type_mismatch"]}
    )
    decision = evaluate_transition(request, _license())
    assert decision.decision == Decision.HUMAN_REVIEW_REQUIRED
    assert decision.rank == Rank.LIKELY


def test_missing_evidence_defers_decision() -> None:
    request = TransitionRequest(**{**_valid_request().__dict__, "evidence_trace": {"trace": "ev-1"}})
    decision = evaluate_transition(request, _license())
    assert decision.decision == Decision.DEFERRED
    assert any(res.stage == FailedStage.EVIDENCE for res in decision.residuals)


def test_metric_cannot_certify_control_without_evidence() -> None:
    request = TransitionRequest(
        **{
            **_valid_request().__dict__,
            "evidence_trace": None,
            "metric_claimed_compliance": True,
            "action_requested": False,
        }
    )
    decision = evaluate_transition(request, _license())
    assert decision.decision == Decision.DEFERRED
    assert any(res.code == "metric_not_judgment" for res in decision.residuals)


def test_action_not_allowed_below_threshold() -> None:
    request = TransitionRequest(
        **{
            **_valid_request().__dict__,
            "requested_rank": Rank.HYPOTHESIS,
            "minimum_action_rank": Rank.VERIFIED,
            "action_requested": True,
        }
    )
    decision = evaluate_transition(request, _license())
    assert decision.decision == Decision.BLOCKED
    assert decision.action_allowed is False
    assert decision.failed_stage == FailedStage.ACTION


def test_valid_transition_allows_delivery() -> None:
    decision = evaluate_transition(_valid_request(), _license())
    assert decision.decision == Decision.ALLOWED
    assert decision.action_allowed is True
    assert decision.rank == Rank.VERIFIED


def test_agents_md_contains_mandatory_constitution_laws() -> None:
    agents_path = Path(__file__).resolve().parents[3] / "AGENTS.md"
    content = agents_path.read_text(encoding="utf-8")
    required_terms = [
        "Origin",
        "BranchLicense",
        "Effective Attribute",
        "Sabab",
        "Conditions",
        "Mani",
        "Qadih",
        "Evidence Trace",
        "Rank",
        "Residuals",
        "Handoff",
        "No metric is allowed to become a compliance judgment by itself",
        "No AI output is allowed to become a decision or action without a governed transition decision",
    ]
    for term in required_terms:
        assert term in content
