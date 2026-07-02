from .contracts import (
    BranchLicense,
    Decision,
    FailedStage,
    Rank,
    Residual,
    ResidualSeverity,
    TransitionDecision,
    TransitionRequest,
)


def evaluate_transition(
    request: TransitionRequest, license: BranchLicense | None
) -> TransitionDecision:
    residuals: list[Residual] = []
    failed_stage: FailedStage | None = None

    if not request.origin:
        residuals.append(
            Residual(FailedStage.ORIGIN, "missing_origin", "Origin is required.", ResidualSeverity.CRITICAL)
        )
        return TransitionDecision(Decision.BLOCKED, FailedStage.ORIGIN, Rank.ZERO, False, residuals)

    if not request.branch:
        residuals.append(
            Residual(
                FailedStage.BRANCH_LICENSE,
                "missing_branch",
                "Branch is required.",
                ResidualSeverity.CRITICAL,
            )
        )
        return TransitionDecision(
            Decision.BLOCKED, FailedStage.BRANCH_LICENSE, Rank.ZERO, False, residuals
        )

    if license is None:
        residuals.append(
            Residual(
                FailedStage.BRANCH_LICENSE,
                "missing_license",
                "BranchLicense is required.",
                ResidualSeverity.CRITICAL,
            )
        )
        return TransitionDecision(
            Decision.BLOCKED, FailedStage.BRANCH_LICENSE, Rank.ZERO, False, residuals
        )

    if license.origin != request.origin or license.branch != request.branch:
        residuals.append(
            Residual(
                FailedStage.BRANCH_LICENSE,
                "license_mismatch",
                "BranchLicense origin/branch must match transition request.",
                ResidualSeverity.CRITICAL,
            )
        )
        return TransitionDecision(
            Decision.BLOCKED, FailedStage.BRANCH_LICENSE, Rank.ZERO, False, residuals
        )

    if not request.effective_attribute:
        residuals.append(
            Residual(
                FailedStage.EFFECTIVE_ATTRIBUTE,
                "missing_effective_attribute",
                "Effective attribute is required.",
                ResidualSeverity.HIGH,
            )
        )
        return TransitionDecision(
            Decision.BLOCKED, FailedStage.EFFECTIVE_ATTRIBUTE, Rank.ZERO, False, residuals
        )

    if not request.sabab:
        residuals.append(
            Residual(
                FailedStage.SABAB,
                "missing_sabab",
                "Sabab is required.",
                ResidualSeverity.HIGH,
            )
        )
        return TransitionDecision(Decision.BLOCKED, FailedStage.SABAB, Rank.ZERO, False, residuals)

    missing_conditions = [
        condition for condition in license.conditions if condition not in request.provided_conditions
    ]
    if missing_conditions:
        failed_stage = FailedStage.CONDITION
        residuals.append(
            Residual(
                FailedStage.CONDITION,
                "missing_conditions",
                f"Missing conditions: {', '.join(missing_conditions)}",
                ResidualSeverity.MEDIUM,
            )
        )

    if request.blockers:
        failed_stage = FailedStage.MANI
        residuals.append(
            Residual(
                FailedStage.MANI,
                "mani_present",
                f"Blockers present: {', '.join(request.blockers)}",
                ResidualSeverity.HIGH,
            )
        )

    evidence_requirements = set(license.evidence_requirements)
    mandatory_evidence_fields = {
        "trace",
        "scope",
        "owner",
        "freshness",
        "control_binding",
    }
    provided_evidence = {
        key for key, value in (request.evidence_trace or {}).items() if str(value).strip()
    }
    has_required_evidence = mandatory_evidence_fields.issubset(provided_evidence) and evidence_requirements.issubset(
        provided_evidence
    )

    if not has_required_evidence:
        failed_stage = FailedStage.EVIDENCE if failed_stage is None else failed_stage
        residuals.append(
            Residual(
                FailedStage.EVIDENCE,
                "insufficient_evidence_trace",
                "Evidence trace is incomplete for governed proof.",
                ResidualSeverity.HIGH,
            )
        )

    if request.metric_claimed_compliance and not has_required_evidence:
        failed_stage = FailedStage.EVIDENCE if failed_stage is None else failed_stage
        residuals.append(
            Residual(
                FailedStage.EVIDENCE,
                "metric_not_judgment",
                "Metric cannot certify compliance without governed evidence.",
                ResidualSeverity.HIGH,
            )
        )

    final_rank = request.requested_rank
    if request.qadih_differences:
        if final_rank >= Rank.VERIFIED:
            final_rank = Rank.LIKELY
        residuals.append(
            Residual(
                FailedStage.QADIH,
                "qadih_difference_detected",
                "Qadih differences require review before verified rank.",
                ResidualSeverity.MEDIUM,
            )
        )

    if request.action_requested and final_rank < request.minimum_action_rank:
        failed_stage = FailedStage.ACTION if failed_stage is None else failed_stage
        residuals.append(
            Residual(
                FailedStage.ACTION,
                "rank_below_action_threshold",
                "Action is blocked because rank is below threshold.",
                ResidualSeverity.HIGH,
            )
        )

    if any(r.stage in {FailedStage.MANI, FailedStage.ACTION} for r in residuals):
        return TransitionDecision(Decision.BLOCKED, failed_stage, final_rank, False, residuals)

    if any(r.stage in {FailedStage.CONDITION, FailedStage.EVIDENCE} for r in residuals):
        return TransitionDecision(Decision.DEFERRED, failed_stage, final_rank, False, residuals)

    if any(r.stage == FailedStage.QADIH for r in residuals):
        return TransitionDecision(
            Decision.HUMAN_REVIEW_REQUIRED,
            FailedStage.QADIH,
            final_rank,
            False,
            residuals,
        )

    action_allowed = not request.action_requested or final_rank >= request.minimum_action_rank
    return TransitionDecision(Decision.ALLOWED, None, final_rank, action_allowed, residuals)
