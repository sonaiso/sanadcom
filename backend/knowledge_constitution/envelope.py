"""The required decision envelope (docs/00_KNOWLEDGE_CONSTITUTION.md §9), produced from kernel objects only.

Every governed judgment must carry these keys. The envelope is a projection: it never computes a new
judgment, never raises rank, and reports ``action_license``/``handoff``/``feedback_requirement`` as
``None`` when the action stage has not been evaluated, so a missing stage is visible, not implied.
"""

from .contracts import ActionDecision, ApprovedKnowledgeContext

REQUIRED_ENVELOPE_KEYS: tuple[str, ...] = (
    "knowledge_context_id",
    "reality_candidate_id",
    "trace_ids",
    "defined_locus_id",
    "domain_contract_id",
    "claim_id",
    "relation_ids",
    "normative_source_ids",
    "applicability_result",
    "evidence_binding_ids",
    "rank",
    "rank_ceiling",
    "failed_stage",
    "residuals",
    "judgment_type",
    "judgment_status",
    "action_license",
    "handoff",
    "transition_trace",
    "feedback_requirement",
)


def decision_envelope(
    context: ApprovedKnowledgeContext,
    action: ActionDecision | None = None,
    *,
    normative_source_ids: tuple[str, ...] = (),
    applicability_result: str | None = None,
) -> dict[str, object]:
    residuals = [
        {"failed_stage": residual.failed_stage.value, "code": residual.code, "description": residual.description,
         "blocking": residual.blocking}
        for residual in context.residuals
    ]
    transition_trace = [stage.value for stage in context.transition_trace]
    envelope: dict[str, object] = {
        "knowledge_context_id": context.knowledge_context_id,
        "reality_candidate_id": context.reality_candidate.reality_candidate_id,
        "trace_ids": [trace.trace_id for trace in context.trace_candidates],
        "defined_locus_id": context.defined_locus.defined_locus_id,
        "domain_contract_id": context.domain_contract.domain_contract_id,
        "claim_id": context.claim_candidate.claim_id,
        "relation_ids": [relation.relation_id for relation in context.relation_candidates],
        "normative_source_ids": list(normative_source_ids),
        "applicability_result": applicability_result,
        "evidence_binding_ids": [binding.evidence_binding_id for binding in context.evidence_bindings],
        "rank": context.rank.name,
        "rank_ceiling": context.rank_ceiling.name,
        "failed_stage": context.failed_stage.value if context.failed_stage else None,
        "residuals": residuals,
        "judgment_type": context.judgment_candidate.judgment_type,
        "judgment_status": context.judgment_candidate.judgment_status.value,
        "action_license": None,
        "handoff": None,
        "transition_trace": transition_trace,
        "feedback_requirement": None,
    }
    if action is not None:
        if action.knowledge_context_id != context.knowledge_context_id:
            raise ValueError("action decision belongs to a different knowledge context")
        license_ = action.action_license
        envelope["action_license"] = {
            "action_license_id": license_.action_license_id,
            "action_type": license_.action_type,
            "granted": license_.granted,
            "minimum_rank": license_.minimum_rank.name,
            "rank_at_licensing": license_.rank_at_licensing.name,
            "failed_stage": license_.failed_stage.value if license_.failed_stage else None,
        }
        envelope["handoff"] = {
            "route": action.handoff.route.value,
            "owner": action.handoff.owner,
            "rationale": action.handoff.rationale,
        }
        envelope["feedback_requirement"] = {
            "required": action.feedback_requirement.required,
            "reality_candidate_id": action.feedback_requirement.reality_candidate_id,
            "action_license_id": action.feedback_requirement.action_license_id,
            "feedback_trace_id": action.feedback_requirement.feedback_trace_id,
        }
        envelope["residuals"] = residuals + [
            {"failed_stage": residual.failed_stage.value, "code": residual.code, "description": residual.description,
             "blocking": residual.blocking}
            for residual in action.residuals
        ]
        envelope["transition_trace"] = transition_trace + [stage.value for stage in action.transition_trace]
        if action.failed_stage is not None and envelope["failed_stage"] is None:
            envelope["failed_stage"] = action.failed_stage.value
    return envelope
