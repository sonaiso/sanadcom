"""The judgment chain of one compliance assessment, built from kernel objects only (slice S6, first screen).

For every assessable requirement of a compliance assessment, this module turns what the platform
already stores (the assessed folder, the requirement, the attached evidences) into the knowledge
kernel's candidates and runs the governed transition:

    RealityCandidate (the assessed folder)
    -> TraceCandidate per evidence (source, scope, owner, freshness, control binding)
    -> DefinedLocus (the folder) -> DomainContract (ecc-v1, relation "supports")
    -> ClaimCandidate ("requirement R is implemented in the locus")
    -> RelationCandidate (locus supports claim, cited traces)
    -> EvidenceBinding per trace -> Rank -> Residuals -> JudgmentCandidate
    -> ActionLicense ("mark requirement implemented", threshold VERIFIED) -> Handoff -> FeedbackRequirement

Nothing here is a compliance judgment. A requirement with no evidence yields no trace candidate, so the kernel
blocks it at TRACE_CANDIDATE (missing_trace_candidates) before any binding is even attempted; a requirement with documentary evidence is at most SUPPORTED, so the action
licence is never granted from documents alone and the handoff is DEFERRAL_QUEUE: that is the
screen's message. The platform's own `result` field is returned beside the chain as
`declared_result`, labelled as a declaration, never merged into the judgment.

No percentage is computed anywhere in this module.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from django.utils import timezone

from knowledge_constitution import (
    ClaimCandidate,
    DefinedLocus,
    DomainContract,
    EvidenceBinding,
    KnowledgeRank,
    RealityCandidate,
    RelationCandidate,
    Residual,
    TraceCandidate,
    decision_envelope,
    evaluate_action_license,
    evaluate_knowledge_transition,
)
from knowledge_constitution.enums import KnowledgeStage

DOMAIN = DomainContract(
    domain_contract_id="ecc-v1",
    governing_vocabulary="nca-ecc",
    admissible_relation_types=("supports",),
    evidence_rules=("provenance_required", "owner_required", "freshness_required"),
    rank_policy="documentary_ceiling_supported",
)

ACTION_TYPE = "mark_requirement_implemented"
ACTION_MIN_RANK = KnowledgeRank.VERIFIED

STAGES = [s.value for s in KnowledgeStage]


@dataclass(frozen=True)
class EvidenceView:
    """What the screen shows for one evidence, with the reason it did or did not become a trace."""

    id: str
    name: str
    status: str
    owner: str
    freshness: str
    expiry: str | None
    became_trace: bool
    reason: str


def _owner_of(evidence) -> str:
    """First owner e-mail; owners are Actors (user, team or entity) and expose their e-mails."""
    actor = evidence.owner.first()
    if actor is None:
        return ""
    specific = actor.specific
    emails = specific.get_emails() if hasattr(specific, "get_emails") else []
    return (emails[0] if emails else "").strip()


def _source_of(evidence) -> str:
    revision = evidence.last_revision  # property on Evidence
    if revision is None:
        return ""
    if getattr(revision, "attachment", None):
        return f"attachment:{revision.attachment.name}"
    if getattr(revision, "link", None):
        return f"link:{revision.link}"
    return ""


def _integrity_ok(evidence) -> bool:
    revision = evidence.last_revision  # property on Evidence
    if revision is None:
        return False
    if getattr(revision, "attachment", None):
        return bool(getattr(revision, "attachment_hash", ""))
    return bool(getattr(revision, "link", ""))


def traces_of(
    requirement_assessment, reality_id: str, today: dt.date
) -> tuple[list[TraceCandidate], list[EvidenceView]]:
    traces: list[TraceCandidate] = []
    views: list[EvidenceView] = []
    for evidence in requirement_assessment.evidences.all().order_by("name"):
        owner = _owner_of(evidence)
        source = _source_of(evidence)
        status = str(evidence.status)
        expiry = evidence.expiry_date
        freshness = (
            evidence.updated_at.date().isoformat() if evidence.updated_at else ""
        )
        reason = ""
        if status == "missing":
            reason = "EVIDENCE_STATUS_MISSING"
        elif not source:
            reason = "EVIDENCE_HAS_NO_ARTIFACT"
        elif not owner:
            reason = "EVIDENCE_HAS_NO_OWNER"
        elif not freshness:
            reason = "EVIDENCE_HAS_NO_FRESHNESS"
        views.append(
            EvidenceView(
                id=str(evidence.id),
                name=evidence.name,
                status=status,
                owner=owner,
                freshness=freshness,
                expiry=expiry.isoformat() if expiry else None,
                became_trace=reason == "",
                reason=reason,
            )
        )
        if reason:
            continue
        traces.append(
            TraceCandidate(
                trace_id=str(evidence.id),
                reality_candidate_id=reality_id,
                source=source,
                scope=str(evidence.folder.name) if evidence.folder_id else "",
                owner=owner,
                freshness=freshness,
                control_binding=requirement_assessment.requirement.urn
                or str(requirement_assessment.requirement_id),
                trace_type="documentary",
                provenance_ok=status != "rejected",
                integrity_ok=_integrity_ok(evidence),
            )
        )
    return traces, views


def _binding(
    trace: TraceCandidate,
    claim_id: str,
    locus_id: str,
    evidence_view: EvidenceView,
    today: dt.date,
) -> EvidenceBinding:
    not_expired = (
        evidence_view.expiry is None
        or dt.date.fromisoformat(evidence_view.expiry) >= today
    )
    return EvidenceBinding(
        evidence_binding_id=f"binding:{trace.trace_id}",
        claim_id=claim_id,
        defined_locus_id=locus_id,
        domain_contract_id=DOMAIN.domain_contract_id,
        trace_ids=(trace.trace_id,),
        provenance_ok=trace.provenance_ok,
        integrity_ok=trace.integrity_ok,
        scope_coverage_ok=True,
        temporal_coverage_ok=not_expired and evidence_view.status != "expired",
        claim_relevance_ok=True,
    )


def chain_for_requirement(
    compliance_assessment, requirement_assessment, today: dt.date | None = None
) -> dict:
    today = today or timezone.localdate()
    folder = compliance_assessment.folder
    requirement = requirement_assessment.requirement
    reality_id = f"folder:{folder.id}"
    locus_id = f"locus:{folder.id}"
    claim_id = f"claim:{requirement.urn or requirement.id}"

    reality = RealityCandidate(
        reality_candidate_id=reality_id,
        reality_type="ORGANIZATIONAL_SCOPE",
        temporal_bounds=str(
            compliance_assessment.version or compliance_assessment.created_at.date()
        ),
        observation_source="platform:folder",
        identity_conditions=("folder_id",),
    )
    traces, views = traces_of(requirement_assessment, reality_id, today)
    view_by_id = {v.id: v for v in views}
    locus = DefinedLocus(
        defined_locus_id=locus_id,
        locus_type="FOLDER",
        reality_candidate_id=reality_id,
        boundaries=str(folder.name),
        applicable_time=reality.temporal_bounds,
    )
    claim = ClaimCandidate(
        claim_id=claim_id,
        defined_locus_id=locus_id,
        predicate=f"requirement {requirement.ref_id or requirement.urn} is implemented in the locus",
        relation_type="supports",
        temporal_scope=reality.temporal_bounds,
        domain_contract_id=DOMAIN.domain_contract_id,
        required_evidence_class="documentary",
    )
    relation = RelationCandidate(
        relation_id=f"relation:{claim_id}",
        source_object_id=locus_id,
        target_object_id=claim_id,
        relation_type="supports",
        domain_contract_id=DOMAIN.domain_contract_id,
        evidence_trace_ids=tuple(t.trace_id for t in traces),
    )
    bindings = tuple(
        _binding(t, claim_id, locus_id, view_by_id[t.trace_id], today) for t in traces
    )

    context = evaluate_knowledge_transition(
        knowledge_context_id=f"kc:{compliance_assessment.id}:{requirement.urn or requirement.id}",
        reality_candidate=reality,
        trace_candidates=tuple(traces),
        defined_locus=locus,
        domain_contract=DOMAIN,
        claim_candidate=claim,
        relation_candidates=(relation,),
        evidence_bindings=bindings,
        requested_rank=KnowledgeRank.SUPPORTED,
    )
    action = evaluate_action_license(
        context=context,
        action_license_id=f"al:{context.knowledge_context_id}",
        action_type=ACTION_TYPE,
        minimum_rank=ACTION_MIN_RANK,
    )
    envelope = decision_envelope(
        context, action, normative_source_ids=("ECC",), applicability_result="origin"
    )

    # stage strip: every stage up to the first failed one is "reached"; the failed one is "blocked"
    failed = envelope["failed_stage"]
    strip = []
    blocked_seen = False
    for stage in STAGES:
        if blocked_seen:
            state = "not_reached"
        elif stage == failed:
            state = "blocked"
            blocked_seen = True
        else:
            state = "reached"
        strip.append({"stage": stage, "state": state})

    non_trace_residuals = [
        {
            "failed_stage": "TRACE_CANDIDATE",
            "code": v.reason,
            "description": f"evidence '{v.name}' did not become a trace",
            "blocking": False,
        }
        for v in views
        if not v.became_trace
    ]
    return {
        "requirement": {
            "id": str(requirement.id),
            "urn": requirement.urn,
            "ref_id": requirement.ref_id,
            "name": requirement.name,
            "assessable": bool(requirement.assessable),
        },
        "declared_result": str(requirement_assessment.result),
        "declared_status": str(requirement_assessment.status),
        "stages": strip,
        "judgment": {
            "status": envelope["judgment_status"],
            "rank": envelope["rank"],
            "rank_ceiling": envelope["rank_ceiling"],
            "failed_stage": failed,
        },
        "action": envelope["action_license"],
        "handoff": envelope["handoff"],
        "feedback_requirement": envelope["feedback_requirement"],
        "residuals": envelope["residuals"] + non_trace_residuals,
        "evidence": [v.__dict__ for v in views],
        "envelope": envelope,
    }


def chain_for_assessment(compliance_assessment, today: dt.date | None = None) -> dict:
    today = today or timezone.localdate()
    rows = []
    for ra in compliance_assessment.get_requirement_assessments(
        include_non_assessable=False
    ):
        rows.append(chain_for_requirement(compliance_assessment, ra, today))
    counts_by_status: dict[str, int] = {}
    counts_by_failed_stage: dict[str, int] = {}
    counts_by_route: dict[str, int] = {}
    for row in rows:
        counts_by_status[row["judgment"]["status"]] = (
            counts_by_status.get(row["judgment"]["status"], 0) + 1
        )
        key = row["judgment"]["failed_stage"] or "NONE"
        counts_by_failed_stage[key] = counts_by_failed_stage.get(key, 0) + 1
        route = row["handoff"]["route"] if row["handoff"] else "NONE"
        counts_by_route[route] = counts_by_route.get(route, 0) + 1
    return {
        "compliance_assessment": {
            "id": str(compliance_assessment.id),
            "name": compliance_assessment.name,
            "framework": {
                "id": str(compliance_assessment.framework.id),
                "name": compliance_assessment.framework.name,
            },
            "folder": {
                "id": str(compliance_assessment.folder.id),
                "name": compliance_assessment.folder.name,
            },
        },
        "domain_contract": DOMAIN.domain_contract_id,
        "action_type": ACTION_TYPE,
        "action_minimum_rank": ACTION_MIN_RANK.name,
        "stages": STAGES,
        "counts": {
            "requirements": len(rows),
            "by_judgment_status": counts_by_status,
            "by_failed_stage": counts_by_failed_stage,
            "by_handoff_route": counts_by_route,
        },
        "requirements": rows,
    }


__all__ = [
    "ACTION_MIN_RANK",
    "ACTION_TYPE",
    "DOMAIN",
    "chain_for_assessment",
    "chain_for_requirement",
]

# Keep the module's own residual type importable for tests that inspect blocking semantics.
_ = Residual
