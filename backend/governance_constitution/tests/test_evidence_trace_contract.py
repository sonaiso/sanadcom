from governance_constitution.contracts import BranchLicense, Rank, TransitionRequest
from governance_constitution.guard import evaluate_transition


def _license() -> BranchLicense:
    return BranchLicense(
        origin="ECC",
        branch="DCC",
        effective_attribute="data_asset_lifecycle",
        sabab="organizational data assets exist",
        conditions=["data_asset_scope_defined"],
        evidence_requirements=("source", "scope", "owner", "freshness", "control_binding"),
    )


def test_guard_accepts_source_without_trace_requirement() -> None:
    request = TransitionRequest(
        origin="ECC",
        branch="DCC",
        effective_attribute="data_asset_lifecycle",
        sabab="organizational data assets exist",
        provided_conditions=["data_asset_scope_defined"],
        evidence_trace={
            "source": "policy-document",
            "scope": "data-platform",
            "owner": "data-owner",
            "freshness": "2026-07-02",
            "control_binding": "DCC-3-2-1",
        },
        requested_rank=Rank.HYPOTHESIS,
    )

    decision = evaluate_transition(request, _license())

    assert all(residual.code != "insufficient_evidence_trace" for residual in decision.residuals)


def test_guard_does_not_accept_trace_only_evidence() -> None:
    request = TransitionRequest(
        origin="ECC",
        branch="DCC",
        effective_attribute="data_asset_lifecycle",
        sabab="organizational data assets exist",
        provided_conditions=["data_asset_scope_defined"],
        evidence_trace={
            "trace": "policy-document",
            "scope": "data-platform",
            "owner": "data-owner",
            "freshness": "2026-07-02",
            "control_binding": "DCC-3-2-1",
        },
        requested_rank=Rank.HYPOTHESIS,
    )

    decision = evaluate_transition(request, _license())

    assert any(residual.code == "insufficient_evidence_trace" for residual in decision.residuals)
