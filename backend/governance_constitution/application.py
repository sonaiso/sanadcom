from dataclasses import dataclass

from knowledge_constitution.contracts import ApprovedKnowledgeContext, EvidenceBinding as KnowledgeEvidenceBinding
from knowledge_constitution.enums import KnowledgeRank

from .contracts import (
    BranchLicense,
    Condition,
    ConstitutionalDecision,
    EvidenceTrace,
    HandoffRule,
    Mani,
    Sabab,
)
from .enums import EvidenceRank


ApplicabilityLicense = BranchLicense


@dataclass(frozen=True)
class GovernanceJudgmentCandidate:
    knowledge_context_id: str
    constitutional_decision: ConstitutionalDecision


def _to_evidence_rank(rank: KnowledgeRank) -> EvidenceRank:
    if rank >= KnowledgeRank.VERIFIED:
        return EvidenceRank.VERIFIED
    if rank >= KnowledgeRank.SUPPORTED:
        return EvidenceRank.SUPPORTED
    if rank >= KnowledgeRank.PLAUSIBLE:
        return EvidenceRank.HYPOTHESIS
    return EvidenceRank.CANDIDATE


def _to_evidence_traces(
    context: ApprovedKnowledgeContext,
    evidence_bindings: tuple[KnowledgeEvidenceBinding, ...],
) -> tuple[EvidenceTrace, ...]:
    trace_index = {trace.trace_id: trace for trace in context.trace_candidates}
    traces: list[EvidenceTrace] = []
    for binding in evidence_bindings:
        for trace_id in binding.trace_ids:
            trace = trace_index.get(trace_id)
            if trace is None:
                raise ValueError(f"trace '{trace_id}' from evidence binding is not present in knowledge context")
            traces.append(
                EvidenceTrace(
                    source=trace.source,
                    scope=trace.scope,
                    owner=trace.owner,
                    freshness=trace.freshness,
                    control_binding=trace.control_binding,
                    evidence_ref=f"{binding.evidence_binding_id}:{trace.trace_id}",
                )
            )
    return tuple(traces)


def evaluate_governance_application(
    *,
    knowledge_context: ApprovedKnowledgeContext,
    applicability_license: ApplicabilityLicense,
    evidence_bindings: tuple[KnowledgeEvidenceBinding, ...],
) -> GovernanceJudgmentCandidate:
    if not knowledge_context.approved:
        raise ValueError("approved knowledge context is required before governance evaluation")
    if not evidence_bindings:
        raise ValueError("governance evaluation requires evidence bindings")

    known_binding_ids = {binding.evidence_binding_id for binding in knowledge_context.evidence_bindings}
    for binding in evidence_bindings:
        if binding.evidence_binding_id not in known_binding_ids:
            raise ValueError("evidence binding must come from approved knowledge context")

    evidence_traces = _to_evidence_traces(knowledge_context, evidence_bindings)
    satisfied_conditions = tuple(
        Condition(condition.condition_id, condition.description, satisfied=True)
        if isinstance(condition, Condition)
        else Condition(str(condition), satisfied=True)
        for condition in applicability_license.conditions
    )
    mani_eval = tuple(
        Mani(blocker.blocker_id, blocker.description, active=blocker.active)
        if isinstance(blocker, Mani)
        else Mani(str(blocker), active=False)
        for blocker in applicability_license.mani
    )

    rank = _to_evidence_rank(min(knowledge_context.rank, knowledge_context.rank_ceiling))
    minimum = applicability_license.rank_policy.minimum_action_rank
    if rank > minimum:
        rank = minimum

    decision = ConstitutionalDecision(
        origin=applicability_license.origin,
        branch=applicability_license.branch_id or applicability_license.branch or "",
        branch_license=applicability_license,
        effective_attribute=applicability_license.effective_attribute or "",
        sabab=applicability_license.sabab or Sabab("derived-from-knowledge-context"),
        conditions_evaluated=satisfied_conditions,
        mani_evaluated=mani_eval,
        qadih_differences=tuple(applicability_license.qadih_differences),
        evidence_traces=evidence_traces,
        rank=rank,
        handoff=HandoffRule(required=False),
    )
    return GovernanceJudgmentCandidate(
        knowledge_context_id=knowledge_context.knowledge_context_id,
        constitutional_decision=decision,
    )
