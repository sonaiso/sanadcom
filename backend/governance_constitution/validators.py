from __future__ import annotations

from dataclasses import replace
from typing import Any

from .enums import DecisionStatus, EvidenceRank, FailedStage

_NCA = "NCA"
_CERTIFIED = "certified"
_APPROVED = "approved"

FORBIDDEN_NCA_WORDING = (
    f"{_CERTIFIED} by {_NCA}",
    f"{_APPROVED} by {_NCA}",
    f"{_NCA} {_CERTIFIED}",
    f"{_NCA} {_APPROVED}",
)


def ensure_branch_license_fields(branch_license: Any) -> None:
    required = {
        "origin": branch_license.origin,
        "branch_id": branch_license.branch_id,
        "effective_attribute": branch_license.effective_attribute,
        "sabab": branch_license.sabab,
        "conditions": branch_license.conditions,
        "mani": branch_license.mani,
        "qadih_differences": branch_license.qadih_differences,
        "evidence_requirements": branch_license.evidence_requirements,
        "rank_policy": branch_license.rank_policy,
        "residual_policy": branch_license.residual_policy,
    }
    missing = [name for name, value in required.items() if value is None or value == ""]
    if missing:
        raise ValueError(f"BranchLicense missing required fields: {', '.join(missing)}")


def ensure_evidence_trace_fields(evidence_trace: Any) -> None:
    required = {
        "source": evidence_trace.source,
        "scope": evidence_trace.scope,
        "owner": evidence_trace.owner,
        "freshness": evidence_trace.freshness,
        "control_binding": evidence_trace.control_binding,
    }
    missing = [name for name, value in required.items() if not value or not str(value).strip()]
    if missing:
        raise ValueError(f"EvidenceTrace missing required fields: {', '.join(missing)}")
    if not evidence_trace.artifact_ref and not evidence_trace.evidence_ref:
        raise ValueError("EvidenceTrace requires artifact_ref or evidence_ref")


def ensure_no_forbidden_nca_wording(text: str) -> None:
    lowered = text.lower()
    for phrase in FORBIDDEN_NCA_WORDING:
        if phrase.lower() in lowered:
            raise ValueError("forbidden NCA approval/certification wording")


def enforce_constitutional_rank_ceiling(
    *, rank: EvidenceRank, evidence_traces: tuple[Any, ...], conditions_evaluated: tuple[Any, ...]
) -> None:
    if rank == EvidenceRank.VERIFIED and not evidence_traces:
        raise ValueError("VERIFIED rank requires evidence traces")
    if rank == EvidenceRank.VERIFIED and evidence_traces and all(
        str(trace.evidence_type).lower() == "policy" for trace in evidence_traces
    ):
        raise ValueError("policy-only evidence cannot produce VERIFIED rank")
    if rank == EvidenceRank.VERIFIED and any(trace.metric_like for trace in evidence_traces):
        raise ValueError("metric evidence is candidate material and cannot produce VERIFIED rank")
    if rank > EvidenceRank.HYPOTHESIS and conditions_evaluated and not all(
        condition.satisfied for condition in conditions_evaluated
    ):
        raise ValueError("unsatisfied conditions cannot produce supported or verified rank")


def derive_decision_status(
    decision: Any, residual_factory: Any
) -> tuple[DecisionStatus, FailedStage | None, tuple[Any, ...], EvidenceRank, Any]:
    residuals = list(decision.residuals)
    rank = decision.rank
    handoff = decision.handoff

    if any(condition.satisfied is None for condition in decision.conditions_evaluated):
        residuals.append(
            residual_factory(
                stage=FailedStage.CONDITIONS,
                code="unknown_condition_state",
                message="condition state is unknown and governance judgment is deferred",
            )
        )
        return DecisionStatus.DEFERRED, FailedStage.CONDITIONS, tuple(residuals), rank, handoff

    if any(condition.satisfied is False for condition in decision.conditions_evaluated):
        residuals.append(
            residual_factory(
                stage=FailedStage.CONDITIONS,
                code="unsatisfied_condition",
                message="at least one governance condition is unsatisfied",
            )
        )
        return DecisionStatus.DEFERRED, FailedStage.CONDITIONS, tuple(residuals), rank, handoff

    if any(mani.active is None for mani in decision.mani_evaluated):
        handoff = replace(handoff, required=True)
        residuals.append(
            residual_factory(
                stage=FailedStage.MANI,
                code="unknown_mani_state",
                message="mani state is unknown and requires human review",
            )
        )
        return DecisionStatus.HUMAN_REVIEW_REQUIRED, FailedStage.MANI, tuple(residuals), rank, handoff

    if any(mani.active for mani in decision.mani_evaluated):
        if not residuals:
            residuals.append(
                residual_factory(
                    stage=FailedStage.MANI,
                    code="active_mani",
                    message="active mani blocks action",
                )
            )
        return DecisionStatus.BLOCKED, FailedStage.MANI, tuple(residuals), rank, handoff

    if not decision.evidence_traces:
        residuals.append(
            residual_factory(
                stage=FailedStage.EVIDENCE_TRACE,
                code="missing_evidence_trace",
                message="missing evidence trace",
            )
        )
        return DecisionStatus.DEFERRED, FailedStage.EVIDENCE_TRACE, tuple(residuals), rank, handoff

    if decision.qadih_differences:
        downgrade = max(item.rank_downgrade_steps for item in decision.qadih_differences)
        rank = EvidenceRank(max(int(EvidenceRank.ZERO), int(rank) - downgrade))
        residuals.append(
            residual_factory(
                stage=FailedStage.QADIH_DIFFERENCE,
                code="qadih_difference_detected",
                message="qadih difference requires governed handling",
            )
        )
        if any(item.requires_human_review for item in decision.qadih_differences):
            handoff = replace(handoff, required=True)
            return (
                DecisionStatus.HUMAN_REVIEW_REQUIRED,
                FailedStage.QADIH_DIFFERENCE,
                tuple(residuals),
                rank,
                handoff,
            )
        return DecisionStatus.DEFERRED, FailedStage.QADIH_DIFFERENCE, tuple(residuals), rank, handoff

    if rank < decision.branch_license.rank_policy.minimum_action_rank:
        residuals.append(
            residual_factory(
                stage=FailedStage.RANK,
                code="rank_below_policy",
                message="rank is below branch license action threshold",
            )
        )
        if rank == EvidenceRank.CANDIDATE:
            return DecisionStatus.CANDIDATE, FailedStage.RANK, tuple(residuals), rank, handoff
        return DecisionStatus.DEFERRED, FailedStage.RANK, tuple(residuals), rank, handoff

    return DecisionStatus.ALLOWED, None, tuple(residuals), rank, handoff


def derive_action_allowed(status: DecisionStatus) -> bool:
    return status == DecisionStatus.ALLOWED
