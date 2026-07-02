from pathlib import Path

import pytest

from governance_constitution.contracts import (
    BranchLicense,
    Condition,
    ConstitutionalDecision,
    EvidenceTrace,
    Mani,
    OriginNode,
    QadihDifference,
    RankPolicy,
    Sabab,
)
from governance_constitution.enums import DecisionStatus, EvidenceRank, FailedStage
from governance_constitution.validators import FORBIDDEN_NCA_WORDING


def _origin() -> OriginNode:
    return OriginNode(origin_id="ECC", title="Essential Cybersecurity Controls")


def _license() -> BranchLicense:
    return BranchLicense(
        origin=_origin(),
        branch_id="DCC",
        effective_attribute="data lifecycle",
        sabab=Sabab("organizational data assets"),
        conditions=(Condition("data_inventory"),),
        mani=(Mani("none"),),
        qadih_differences=(),
        evidence_requirements=("source", "scope", "owner", "freshness", "control_binding"),
        rank_policy=RankPolicy(minimum_action_rank=EvidenceRank.SUPPORTED),
        residual_policy="record_all_failures",
    )


def _evidence(**kwargs: object) -> EvidenceTrace:
    payload = {
        "source": "policy-repo",
        "scope": "org",
        "owner": "grc-owner",
        "freshness": "2026-07-01",
        "control_binding": "DCC-01",
        "artifact_ref": "artifact://policy/001",
        "evidence_type": "artifact",
        "metric_like": False,
    }
    payload.update(kwargs)
    return EvidenceTrace(**payload)


def _decision(**kwargs: object) -> ConstitutionalDecision:
    payload = {
        "origin": _origin(),
        "branch": "DCC",
        "branch_license": _license(),
        "effective_attribute": "data lifecycle",
        "sabab": Sabab("organizational data assets"),
        "conditions_evaluated": (Condition("data_inventory", satisfied=True),),
        "mani_evaluated": (),
        "qadih_differences": (),
        "evidence_traces": (_evidence(),),
        "rank": EvidenceRank.SUPPORTED,
    }
    payload.update(kwargs)
    return ConstitutionalDecision(**payload)


def test_no_branch_license_without_origin() -> None:
    with pytest.raises(ValueError):
        BranchLicense(
            origin=None,
            branch_id="DCC",
            effective_attribute="attr",
            sabab=Sabab("cause"),
            conditions=(Condition("c1"),),
            mani=(Mani("m1"),),
            qadih_differences=(),
            evidence_requirements=("source",),
            rank_policy=RankPolicy(),
            residual_policy="policy",
        )


def test_no_branch_license_without_effective_attribute() -> None:
    with pytest.raises(ValueError):
        BranchLicense(
            origin=_origin(),
            branch_id="DCC",
            effective_attribute=None,
            sabab=Sabab("cause"),
            conditions=(Condition("c1"),),
            mani=(Mani("m1"),),
            qadih_differences=(),
            evidence_requirements=("source",),
            rank_policy=RankPolicy(),
            residual_policy="policy",
        )


def test_no_branch_license_without_sabab() -> None:
    with pytest.raises(ValueError):
        BranchLicense(
            origin=_origin(),
            branch_id="DCC",
            effective_attribute="attr",
            sabab=None,
            conditions=(Condition("c1"),),
            mani=(Mani("m1"),),
            qadih_differences=(),
            evidence_requirements=("source",),
            rank_policy=RankPolicy(),
            residual_policy="policy",
        )


def test_no_branch_license_without_conditions_field() -> None:
    with pytest.raises(ValueError):
        BranchLicense(
            origin=_origin(),
            branch_id="DCC",
            effective_attribute="attr",
            sabab=Sabab("cause"),
            conditions=None,
            mani=(Mani("m1"),),
            qadih_differences=(),
            evidence_requirements=("source",),
            rank_policy=RankPolicy(),
            residual_policy="policy",
        )


def test_no_branch_license_without_mani_field() -> None:
    with pytest.raises(ValueError):
        BranchLicense(
            origin=_origin(),
            branch_id="DCC",
            effective_attribute="attr",
            sabab=Sabab("cause"),
            conditions=(Condition("c1"),),
            mani=None,
            qadih_differences=(),
            evidence_requirements=("source",),
            rank_policy=RankPolicy(),
            residual_policy="policy",
        )


def test_no_branch_license_without_qadih_field() -> None:
    with pytest.raises(ValueError):
        BranchLicense(
            origin=_origin(),
            branch_id="DCC",
            effective_attribute="attr",
            sabab=Sabab("cause"),
            conditions=(Condition("c1"),),
            mani=(Mani("m1"),),
            qadih_differences=None,
            evidence_requirements=("source",),
            rank_policy=RankPolicy(),
            residual_policy="policy",
        )


def test_no_evidence_trace_without_required_fields() -> None:
    with pytest.raises(ValueError):
        EvidenceTrace(
            source="repo",
            scope="",
            owner="owner",
            freshness="",
            control_binding="",
            artifact_ref=None,
            evidence_ref=None,
        )


def test_metric_evidence_cannot_become_compliance_decision() -> None:
    with pytest.raises(ValueError):
        _decision(evidence_traces=(_evidence(metric_like=True),), rank=EvidenceRank.VERIFIED)


def test_policy_evidence_alone_cannot_produce_verified_rank() -> None:
    with pytest.raises(ValueError):
        _decision(evidence_traces=(_evidence(evidence_type="policy"),), rank=EvidenceRank.VERIFIED)


def test_active_mani_produces_blocked_and_action_false() -> None:
    decision = _decision(mani_evaluated=(Mani("missing-owner", active=True),), rank=EvidenceRank.SUPPORTED)
    assert decision.status == DecisionStatus.BLOCKED
    assert decision.action_allowed is False
    assert decision.failed_stage == FailedStage.MANI
    assert decision.residuals


def test_missing_evidence_produces_deferred_with_residuals() -> None:
    decision = _decision(evidence_traces=(), rank=EvidenceRank.CANDIDATE)
    assert decision.status in {DecisionStatus.CANDIDATE, DecisionStatus.DEFERRED}
    assert decision.action_allowed is False
    assert decision.failed_stage == FailedStage.EVIDENCE_TRACE
    assert any(res.code == "missing_evidence_trace" for res in decision.residuals)


def test_qadih_difference_downgrades_rank_or_requires_handoff() -> None:
    decision = _decision(
        rank=EvidenceRank.VERIFIED,
        qadih_differences=(QadihDifference("asset-mismatch", rank_downgrade_steps=1, requires_human_review=True),),
    )
    assert decision.rank < EvidenceRank.VERIFIED
    assert decision.status == DecisionStatus.HUMAN_REVIEW_REQUIRED
    assert decision.handoff.required is True


def test_direct_action_allowed_true_cannot_be_constructed() -> None:
    with pytest.raises(TypeError):
        ConstitutionalDecision(
            origin=_origin(),
            branch="DCC",
            branch_license=_license(),
            effective_attribute="data lifecycle",
            sabab=Sabab("organizational data assets"),
            conditions_evaluated=(Condition("data_inventory", satisfied=True),),
            mani_evaluated=(),
            qadih_differences=(),
            evidence_traces=(_evidence(),),
            rank=EvidenceRank.SUPPORTED,
            action_allowed=True,
        )


def test_no_forbidden_nca_wording_in_runtime_or_docs() -> None:
    root = Path(__file__).resolve().parents[2]
    targets = [
        root / "governance_constitution" / "contracts.py",
        root / "governance_constitution" / "README.md",
    ]
    for target in targets:
        text = target.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_NCA_WORDING:
            assert phrase not in text
