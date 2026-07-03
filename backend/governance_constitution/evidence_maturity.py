from dataclasses import dataclass

EVIDENCE_MISSING = "evidence_missing"
EVIDENCE_DRAFT = "evidence_draft"
EVIDENCE_SUBMITTED = "evidence_submitted"
EVIDENCE_ATTESTED = "evidence_attested"
EVIDENCE_VALIDATED = "evidence_validated"
EVIDENCE_EXPIRED = "evidence_expired"
EVIDENCE_REJECTED = "evidence_rejected"
EVIDENCE_CONFLICTING = "evidence_conflicting"


@dataclass(frozen=True)
class EvidenceMaturityContext:
    """Operational input context for lightweight evidence maturity evaluation."""

    evidence_refs: tuple[str, ...] = ()
    evidence_type: str | None = None
    submitted: bool = False
    attested_by_owner: bool = False
    validated_by_reviewer: bool = False
    rejected: bool = False
    conflicting: bool = False
    expired: bool = False
    artifact_ref: str | None = None
    owner: str | None = None
    scope: str | None = None
    control_binding: str | None = None
    freshness: str | None = None


@dataclass(frozen=True)
class EvidenceMaturityResult:
    """
    Operational evidence maturity output without compliance or approval judgments.

    `required` indicates whether additional operational follow-up is still required.
    It becomes False only at `evidence_validated`.
    """

    state: str
    required: bool
    missing_fields: tuple[str, ...]
    reason_codes: tuple[str, ...]
    audit_notes: tuple[str, ...]
    blocks_validation: bool
    human_review_required: bool


def _trace_missing_fields(context: EvidenceMaturityContext) -> tuple[str, ...]:
    """Return missing evidence trace fields required for operational review readiness."""

    missing: list[str] = []
    if not context.owner:
        missing.append("owner")
    if not context.scope:
        missing.append("scope")
    if not context.control_binding:
        missing.append("control_binding")
    if not context.freshness:
        missing.append("freshness")
    return tuple(missing)


def evaluate_evidence_maturity(context: EvidenceMaturityContext) -> EvidenceMaturityResult:
    """
    Evaluate operational evidence maturity state.

    The output classifies evidence readiness for internal workflow only and never emits
    compliance, certification, approval, or action-allowance decisions.
    """

    missing_fields = _trace_missing_fields(context)
    audit_notes = tuple(f"missing_trace_field:{field}" for field in missing_fields)

    if not context.evidence_refs and not context.artifact_ref:
        return EvidenceMaturityResult(
            state=EVIDENCE_MISSING,
            required=True,
            missing_fields=missing_fields,
            reason_codes=("evidence_absent",),
            audit_notes=audit_notes,
            blocks_validation=True,
            human_review_required=False,
        )

    if context.rejected:
        return EvidenceMaturityResult(
            state=EVIDENCE_REJECTED,
            required=True,
            missing_fields=missing_fields,
            reason_codes=("evidence_rejected",),
            audit_notes=audit_notes,
            blocks_validation=True,
            human_review_required=False,
        )

    if context.conflicting:
        return EvidenceMaturityResult(
            state=EVIDENCE_CONFLICTING,
            required=True,
            missing_fields=missing_fields,
            reason_codes=("evidence_conflicting",),
            audit_notes=audit_notes,
            blocks_validation=True,
            human_review_required=True,
        )

    if context.expired:
        return EvidenceMaturityResult(
            state=EVIDENCE_EXPIRED,
            required=True,
            missing_fields=missing_fields,
            reason_codes=("evidence_expired",),
            audit_notes=audit_notes,
            blocks_validation=True,
            human_review_required=False,
        )

    if not context.submitted and (context.artifact_ref or context.evidence_refs):
        return EvidenceMaturityResult(
            state=EVIDENCE_DRAFT,
            required=True,
            missing_fields=missing_fields,
            reason_codes=("evidence_not_submitted",),
            audit_notes=audit_notes,
            blocks_validation=True,
            human_review_required=False,
        )

    if context.submitted and not context.attested_by_owner:
        return EvidenceMaturityResult(
            state=EVIDENCE_SUBMITTED,
            required=True,
            missing_fields=missing_fields,
            reason_codes=("owner_attestation_pending",),
            audit_notes=audit_notes,
            blocks_validation=True,
            human_review_required=False,
        )

    if context.attested_by_owner and not context.validated_by_reviewer:
        return EvidenceMaturityResult(
            state=EVIDENCE_ATTESTED,
            required=True,
            missing_fields=missing_fields,
            reason_codes=("reviewer_validation_pending",),
            audit_notes=audit_notes,
            blocks_validation=True,
            human_review_required=False,
        )

    return EvidenceMaturityResult(
        state=EVIDENCE_VALIDATED,
        required=False,
        missing_fields=missing_fields,
        reason_codes=("internal_validation_complete",),
        audit_notes=(*audit_notes, "internal_validation_only_not_compliance_decision"),
        blocks_validation=False,
        human_review_required=False,
    )
