from dataclasses import dataclass

from knowledge_constitution.contracts import ApprovedKnowledgeContext, EvidenceBinding as KnowledgeEvidenceBinding
from knowledge_constitution.enums import KnowledgeRank

from .contracts import (
    BranchLicense,
    Condition,
    ConstitutionalDecision,
    EvidenceTrace,
    GovernanceApplicabilityBinding,
    HandoffRule,
    Mani,
    Residual,
    ResidualSeverity,
    Sabab,
)
from .enums import EvidenceRank, FailedStage


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


def _residual(stage: FailedStage, code: str, message: str, severity: ResidualSeverity = ResidualSeverity.MEDIUM) -> Residual:
    return Residual(stage=stage, code=code, message=message, severity=severity, exception_recorded=True)


def _condition_key(condition: Condition | str) -> str:
    if isinstance(condition, Condition):
        return condition.condition_id
    return str(condition)


def _mani_key(mani: Mani | str) -> str:
    if isinstance(mani, Mani):
        return mani.blocker_id
    return str(mani)


def _to_condition(condition: Condition | str, state: bool | None) -> Condition:
    if isinstance(condition, Condition):
        return Condition(condition.condition_id, condition.description, satisfied=state)
    return Condition(str(condition), satisfied=state)


def _to_mani(blocker: Mani | str, state: bool | None) -> Mani:
    if isinstance(blocker, Mani):
        return Mani(blocker.blocker_id, blocker.description, active=state)
    return Mani(str(blocker), active=state)


def evaluate_governance_application(
    *,
    knowledge_context: ApprovedKnowledgeContext,
    applicability_license: ApplicabilityLicense,
    applicability_binding: GovernanceApplicabilityBinding,
    evidence_binding_ids: tuple[str, ...] | None = None,
    evidence_bindings: tuple[KnowledgeEvidenceBinding, ...] | None = None,
    condition_states: dict[str, bool | None] | None = None,
    mani_states: dict[str, bool | None] | None = None,
) -> GovernanceJudgmentCandidate:
    if not knowledge_context.approved:
        raise ValueError("approved knowledge context is required before governance evaluation")

    if evidence_bindings is None and not evidence_binding_ids:
        raise ValueError("governance evaluation requires evidence bindings")

    condition_states = condition_states or {}
    mani_states = mani_states or {}
    residuals: list[Residual] = []

    if applicability_binding.knowledge_context_id != knowledge_context.knowledge_context_id:
        residuals.append(
            _residual(
                FailedStage.BRANCH_LICENSE,
                "knowledge_context_binding_mismatch",
                "governance applicability binding must reference the approved knowledge context",
            )
        )

    if applicability_binding.branch_id != applicability_license.branch_id:
        residuals.append(
            _residual(
                FailedStage.BRANCH_LICENSE,
                "foreign_branch_license_binding",
                "governance applicability binding branch must match branch license",
            )
        )

    if applicability_binding.normative_source_id != applicability_license.origin.origin_id:
        residuals.append(
            _residual(
                FailedStage.ORIGIN,
                "normative_source_mismatch",
                "governance applicability binding normative source must match branch license origin",
            )
        )

    if applicability_binding.defined_locus_id != knowledge_context.defined_locus.defined_locus_id:
        residuals.append(
            _residual(
                FailedStage.EVIDENCE_TRACE,
                "binding_locus_mismatch",
                "governance applicability binding locus must match approved knowledge context locus",
            )
        )

    if applicability_binding.domain_contract_id != knowledge_context.domain_contract.domain_contract_id:
        residuals.append(
            _residual(
                FailedStage.EVIDENCE_TRACE,
                "binding_domain_mismatch",
                "governance applicability binding domain must match approved knowledge context domain",
            )
        )

    if applicability_binding.applicability_claim_id != knowledge_context.claim_candidate.claim_id:
        residuals.append(
            _residual(
                FailedStage.EVIDENCE_TRACE,
                "binding_claim_mismatch",
                "governance applicability binding claim must match approved knowledge context claim",
            )
        )

    if applicability_binding.effective_attribute_claim_id != knowledge_context.claim_candidate.claim_id:
        residuals.append(
            _residual(
                FailedStage.EFFECTIVE_ATTRIBUTE,
                "effective_attribute_claim_mismatch",
                "effective attribute claim must be proven by approved knowledge context claim",
            )
        )

    if applicability_binding.sabab_claim_id != knowledge_context.claim_candidate.claim_id:
        residuals.append(
            _residual(
                FailedStage.SABAB,
                "sabab_claim_mismatch",
                "sabab claim must be proven by approved knowledge context claim",
            )
        )

    if applicability_license.sabab is None:
        residuals.append(
            _residual(
                FailedStage.SABAB,
                "applicability_sabab_not_proven",
                "governance applicability requires an explicit sabab",
            )
        )

    if knowledge_context.claim_candidate.relation_type.lower() != "supports":
        residuals.append(
            _residual(
                FailedStage.EVIDENCE_TRACE,
                "claim_relation_not_applicable",
                "approved knowledge claim relation must support governance applicability judgments",
            )
        )

    canonical_bindings = {binding.evidence_binding_id: binding for binding in knowledge_context.evidence_bindings}
    selected_ids = evidence_binding_ids or tuple(binding.evidence_binding_id for binding in evidence_bindings or ())
    selected_bindings: list[KnowledgeEvidenceBinding] = []
    for binding_id in selected_ids:
        canonical = canonical_bindings.get(binding_id)
        if canonical is None:
            residuals.append(
                _residual(
                    FailedStage.EVIDENCE_TRACE,
                    "foreign_evidence_binding",
                    "evidence binding id is not issued by the approved knowledge context",
                )
            )
            continue
        selected_bindings.append(canonical)

    if evidence_bindings:
        for provided in evidence_bindings:
            canonical = canonical_bindings.get(provided.evidence_binding_id)
            if canonical is None:
                continue
            if provided != canonical:
                residuals.append(
                    _residual(
                        FailedStage.EVIDENCE_TRACE,
                        "mutated_evidence_binding",
                        "foreign or mutated evidence binding payload is not allowed",
                    )
                )

    selected_binding_ids = tuple(binding.evidence_binding_id for binding in selected_bindings)
    if applicability_binding.evidence_binding_ids and set(applicability_binding.evidence_binding_ids) != set(selected_binding_ids):
        residuals.append(
            _residual(
                FailedStage.EVIDENCE_TRACE,
                "applicability_binding_evidence_set_mismatch",
                "governance applicability binding evidence set must match selected approved evidence bindings",
            )
        )

    for binding in selected_bindings:
        if binding.claim_id != knowledge_context.claim_candidate.claim_id:
            residuals.append(
                _residual(
                    FailedStage.EVIDENCE_TRACE,
                    "binding_claim_must_match_context_claim",
                    "evidence binding claim must match approved knowledge context claim",
                )
            )
        if binding.defined_locus_id != knowledge_context.defined_locus.defined_locus_id:
            residuals.append(
                _residual(
                    FailedStage.EVIDENCE_TRACE,
                    "binding_locus_must_match_context_locus",
                    "evidence binding locus must match approved knowledge context locus",
                )
            )
        if binding.domain_contract_id != knowledge_context.domain_contract.domain_contract_id:
            residuals.append(
                _residual(
                    FailedStage.EVIDENCE_TRACE,
                    "binding_domain_must_match_context_domain",
                    "evidence binding domain must match approved knowledge context domain",
                )
            )

    evidence_traces = _to_evidence_traces(knowledge_context, tuple(selected_bindings)) if selected_bindings else ()
    evaluated_conditions = tuple(
        _to_condition(condition, condition_states.get(_condition_key(condition)))
        for condition in applicability_license.conditions
    )
    mani_eval = tuple(
        _to_mani(blocker, mani_states.get(_mani_key(blocker)))
        for blocker in applicability_license.mani
    )

    rank = _to_evidence_rank(min(knowledge_context.rank, knowledge_context.rank_ceiling))

    decision = ConstitutionalDecision(
        origin=applicability_license.origin,
        branch=applicability_license.branch_id or applicability_license.branch or "",
        branch_license=applicability_license,
        effective_attribute=applicability_license.effective_attribute or "",
        sabab=applicability_license.sabab if applicability_license.sabab is not None else Sabab("missing_sabab"),
        conditions_evaluated=evaluated_conditions,
        mani_evaluated=mani_eval,
        qadih_differences=tuple(applicability_license.qadih_differences),
        evidence_traces=evidence_traces,
        rank=rank,
        residuals=tuple(residuals),
        handoff=HandoffRule(required=False),
    )
    return GovernanceJudgmentCandidate(
        knowledge_context_id=knowledge_context.knowledge_context_id,
        constitutional_decision=decision,
    )
