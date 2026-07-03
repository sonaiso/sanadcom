from dataclasses import dataclass

from .evidence_maturity import (
    EVIDENCE_ATTESTED,
    EVIDENCE_CONFLICTING,
    EVIDENCE_DRAFT,
    EVIDENCE_EXPIRED,
    EVIDENCE_MISSING,
    EVIDENCE_REJECTED,
    EVIDENCE_SUBMITTED,
    EVIDENCE_VALIDATED,
    EvidenceMaturityResult,
)

EVIDENCE_REQUEST = "evidence_request"
SUBMIT_EVIDENCE_TASK = "submit_evidence_task"
OWNER_ATTESTATION_TASK = "owner_attestation_task"
REVIEWER_VALIDATION_TASK = "reviewer_validation_task"
EVIDENCE_REFRESH_TASK = "evidence_refresh_task"
CORRECTIVE_EVIDENCE_TASK = "corrective_evidence_task"
AUDIT_REVIEW_TASK = "audit_review_task"
NO_FOLLOWUP_REQUIRED = "no_followup_required"


@dataclass(frozen=True)
class EvidenceFollowupTask:
    task_type: str
    required: bool
    blocks_validation: bool
    human_review_required: bool
    owner_hint: str | None
    required_inputs: tuple[str, ...]
    reason_codes: tuple[str, ...]
    audit_notes: tuple[str, ...]
    source_state: str


def plan_evidence_followup(result: EvidenceMaturityResult) -> EvidenceFollowupTask:
    required_inputs = result.missing_fields

    if result.state == EVIDENCE_MISSING:
        return EvidenceFollowupTask(
            task_type=EVIDENCE_REQUEST,
            required=True,
            blocks_validation=True,
            human_review_required=False,
            owner_hint=None,
            required_inputs=required_inputs,
            reason_codes=result.reason_codes,
            audit_notes=result.audit_notes,
            source_state=result.state,
        )

    if result.state == EVIDENCE_DRAFT:
        return EvidenceFollowupTask(
            task_type=SUBMIT_EVIDENCE_TASK,
            required=True,
            blocks_validation=True,
            human_review_required=False,
            owner_hint=None,
            required_inputs=required_inputs,
            reason_codes=result.reason_codes,
            audit_notes=result.audit_notes,
            source_state=result.state,
        )

    if result.state == EVIDENCE_SUBMITTED:
        return EvidenceFollowupTask(
            task_type=OWNER_ATTESTATION_TASK,
            required=True,
            blocks_validation=True,
            human_review_required=False,
            owner_hint="control_owner",
            required_inputs=required_inputs,
            reason_codes=result.reason_codes,
            audit_notes=result.audit_notes,
            source_state=result.state,
        )

    if result.state == EVIDENCE_ATTESTED:
        return EvidenceFollowupTask(
            task_type=REVIEWER_VALIDATION_TASK,
            required=True,
            blocks_validation=True,
            human_review_required=False,
            owner_hint="evidence_reviewer",
            required_inputs=required_inputs,
            reason_codes=result.reason_codes,
            audit_notes=result.audit_notes,
            source_state=result.state,
        )

    if result.state == EVIDENCE_EXPIRED:
        return EvidenceFollowupTask(
            task_type=EVIDENCE_REFRESH_TASK,
            required=True,
            blocks_validation=True,
            human_review_required=False,
            owner_hint=None,
            required_inputs=required_inputs,
            reason_codes=result.reason_codes,
            audit_notes=result.audit_notes,
            source_state=result.state,
        )

    if result.state == EVIDENCE_REJECTED:
        return EvidenceFollowupTask(
            task_type=CORRECTIVE_EVIDENCE_TASK,
            required=True,
            blocks_validation=True,
            human_review_required=False,
            owner_hint=None,
            required_inputs=required_inputs,
            reason_codes=result.reason_codes,
            audit_notes=result.audit_notes,
            source_state=result.state,
        )

    if result.state == EVIDENCE_CONFLICTING:
        return EvidenceFollowupTask(
            task_type=AUDIT_REVIEW_TASK,
            required=True,
            blocks_validation=True,
            human_review_required=True,
            owner_hint=None,
            required_inputs=required_inputs,
            reason_codes=result.reason_codes,
            audit_notes=result.audit_notes,
            source_state=result.state,
        )

    if result.state == EVIDENCE_VALIDATED:
        return EvidenceFollowupTask(
            task_type=NO_FOLLOWUP_REQUIRED,
            required=False,
            blocks_validation=False,
            human_review_required=False,
            owner_hint=None,
            required_inputs=(),
            reason_codes=result.reason_codes,
            audit_notes=result.audit_notes,
            source_state=result.state,
        )

    raise ValueError(f"unknown evidence maturity state: {result.state}")
