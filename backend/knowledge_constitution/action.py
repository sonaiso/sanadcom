"""Stages 11-14 of the knowledge transition chain: action licence, handoff, feedback trace, reality re-evaluation.

Constitutional basis (docs/00_KNOWLEDGE_CONSTITUTION.md):
- "No judgment directly becomes an action."            -> evaluate_action_license is a separate transition.
- "No action is allowed when ... rank is below the action threshold."
- "No action is complete without feedback trace."       -> every granted licence carries a FeedbackRequirement.
- Stage 14 "Reality Re-evaluation"                      -> record_feedback yields a new RealityCandidate or residuals.

The default outcome of every transition here is prohibited; a licence is granted only when every gate passes.
"""

from .contracts import (
    ActionDecision,
    ActionLicense,
    ApprovedKnowledgeContext,
    FeedbackRequirement,
    FeedbackResult,
    FeedbackTrace,
    HandoffDecision,
    RealityCandidate,
    Residual,
)
from .enums import HandoffRoute, KnowledgeRank, KnowledgeStage

ACTION_TRANSITION_TRACE: tuple[KnowledgeStage, ...] = (
    KnowledgeStage.JUDGMENT_CANDIDATE,
    KnowledgeStage.ACTION_LICENSE,
    KnowledgeStage.HANDOFF,
)

FEEDBACK_TRANSITION_TRACE: tuple[KnowledgeStage, ...] = (
    KnowledgeStage.ACTION_LICENSE,
    KnowledgeStage.FEEDBACK_TRACE,
    KnowledgeStage.REALITY_REEVALUATION,
)


def evaluate_action_license(
    *,
    context: ApprovedKnowledgeContext,
    action_license_id: str,
    action_type: str,
    minimum_rank: KnowledgeRank = KnowledgeRank.VERIFIED,
    active_blockers: tuple[str, ...] = (),
    human_owner: str | None = None,
) -> ActionDecision:
    """Decide whether a judgment candidate may become an action, and where it is handed off.

    ``context`` is the output of ``evaluate_knowledge_transition``. ``active_blockers`` are mani
    identifiers that are known to be active at licensing time (the caller supplies them; this
    function never infers that a blocker is inactive from its absence).
    """
    residuals: list[Residual] = []

    if not context.approved:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.ACTION_LICENSE,
                code="judgment_not_approved",
                description="The judgment candidate is blocked or unapproved; no action licence can be derived from it.",
            )
        )

    unresolved = tuple(residual for residual in context.residuals if residual.blocking)
    if unresolved:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.ACTION_LICENSE,
                code="unresolved_blocking_residuals",
                description=f"{len(unresolved)} blocking residual(s) remain on the knowledge context.",
            )
        )

    effective_rank = min(context.rank, context.rank_ceiling)
    if effective_rank < minimum_rank:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.ACTION_LICENSE,
                code="rank_below_action_threshold",
                description=(
                    f"Rank {effective_rank.name} is below the action threshold {minimum_rank.name}; "
                    "rank is bounded by evidence and is never raised to permit an action."
                ),
            )
        )

    for blocker in active_blockers:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.ACTION_LICENSE,
                code=f"active_blocker:{blocker}",
                description=f"Active blocker (mani) '{blocker}' prevents the action.",
            )
        )

    blocking = tuple(residual for residual in residuals if residual.blocking)
    granted = len(blocking) == 0
    failed_stage = blocking[0].failed_stage if blocking else None

    license_ = ActionLicense(
        action_license_id=action_license_id,
        knowledge_context_id=context.knowledge_context_id,
        action_type=action_type,
        minimum_rank=minimum_rank,
        rank_at_licensing=effective_rank,
        granted=granted,
        failed_stage=failed_stage,
        residuals=tuple(residuals),
    )

    handoff = _route(context=context, granted=granted, residuals=blocking, human_owner=human_owner)

    feedback_requirement = FeedbackRequirement(
        required=granted,
        reality_candidate_id=context.reality_candidate.reality_candidate_id,
        action_license_id=action_license_id if granted else None,
    )

    return ActionDecision(
        knowledge_context_id=context.knowledge_context_id,
        action_license=license_,
        handoff=handoff,
        feedback_requirement=feedback_requirement,
        residuals=tuple(residuals),
        failed_stage=failed_stage,
        transition_trace=ACTION_TRANSITION_TRACE,
    )


def _route(
    *,
    context: ApprovedKnowledgeContext,
    granted: bool,
    residuals: tuple[Residual, ...],
    human_owner: str | None,
) -> HandoffDecision:
    if granted:
        return HandoffDecision(
            route=HandoffRoute.AUTOMATION,
            owner=human_owner,
            rationale="Action licence granted; execution may proceed under its feedback requirement.",
        )
    codes = {residual.code for residual in residuals}
    only_rank = codes == {"rank_below_action_threshold"}
    if only_rank and context.approved:
        return HandoffDecision(
            route=HandoffRoute.DEFERRAL_QUEUE,
            owner=human_owner,
            rationale="Judgment is supported but rank is below the action threshold; wait for stronger evidence bindings.",
        )
    return HandoffDecision(
        route=HandoffRoute.HUMAN_REVIEW,
        owner=human_owner,
        rationale="Blocked judgment, unresolved residuals or active blockers require human review; nothing is executed.",
    )


def record_feedback(
    *,
    decision: ActionDecision,
    feedback: FeedbackTrace,
    reality_type: str,
    identity_conditions: tuple[str, ...] = (),
) -> FeedbackResult:
    """Close the loop: bind an observed effect to the licence that caused it and re-open reality as a new candidate.

    The re-evaluated reality is a *candidate* again; it earns nothing from the action that produced it.
    """
    residuals: list[Residual] = []

    if not decision.action_license.granted:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.FEEDBACK_TRACE,
                code="feedback_for_ungranted_action",
                description="Feedback cannot be recorded for an action that was never licensed.",
            )
        )
    if feedback.action_license_id != decision.action_license.action_license_id:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.FEEDBACK_TRACE,
                code="feedback_license_mismatch",
                description="Feedback trace references a different action licence.",
            )
        )
    if feedback.reality_candidate_id != decision.feedback_requirement.reality_candidate_id:
        residuals.append(
            Residual(
                failed_stage=KnowledgeStage.FEEDBACK_TRACE,
                code="feedback_reality_mismatch",
                description="Feedback trace observes a different reality candidate than the one acted upon.",
            )
        )

    blocking = tuple(residual for residual in residuals if residual.blocking)
    if blocking:
        return FeedbackResult(
            accepted=False,
            residuals=tuple(residuals),
            failed_stage=blocking[0].failed_stage,
            reality_reevaluation=None,
            transition_trace=FEEDBACK_TRANSITION_TRACE,
        )

    reevaluation = RealityCandidate(
        reality_candidate_id=feedback.reality_candidate_id,
        reality_type=reality_type,
        temporal_bounds=feedback.observed_at,
        observation_source=feedback.observation_source,
        identity_conditions=identity_conditions,
        unresolved_identity_residuals=(),
    )
    return FeedbackResult(
        accepted=True,
        residuals=tuple(residuals),
        failed_stage=None,
        reality_reevaluation=reevaluation,
        transition_trace=FEEDBACK_TRANSITION_TRACE,
    )
