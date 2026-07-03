from dataclasses import asdict
from pathlib import Path

from governance_constitution.evidence_followup import (
    AUDIT_REVIEW_TASK,
    CORRECTIVE_EVIDENCE_TASK,
    EVIDENCE_REQUEST,
    EVIDENCE_REFRESH_TASK,
    NO_FOLLOWUP_REQUIRED,
    OWNER_ATTESTATION_TASK,
    REVIEWER_VALIDATION_TASK,
    SUBMIT_EVIDENCE_TASK,
    plan_evidence_followup,
)
from governance_constitution.evidence_maturity import EvidenceMaturityContext, evaluate_evidence_maturity


def test_missing_evidence_creates_evidence_request() -> None:
    result = evaluate_evidence_maturity(EvidenceMaturityContext())
    task = plan_evidence_followup(result)
    assert task.source_state == "evidence_missing"
    assert task.task_type == EVIDENCE_REQUEST
    assert task.required is True
    assert task.blocks_validation is True


def test_draft_evidence_creates_submit_task() -> None:
    result = evaluate_evidence_maturity(EvidenceMaturityContext(evidence_refs=("ev-1",)))
    task = plan_evidence_followup(result)
    assert task.source_state == "evidence_draft"
    assert task.task_type == SUBMIT_EVIDENCE_TASK
    assert task.required is True
    assert task.blocks_validation is True


def test_submitted_evidence_creates_owner_attestation_task() -> None:
    result = evaluate_evidence_maturity(EvidenceMaturityContext(evidence_refs=("ev-1",), submitted=True))
    task = plan_evidence_followup(result)
    assert task.source_state == "evidence_submitted"
    assert task.task_type == OWNER_ATTESTATION_TASK
    assert task.owner_hint == "control_owner"
    assert task.required is True
    assert task.blocks_validation is True


def test_attested_evidence_creates_reviewer_validation_task() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
            attested_by_owner=True,
        )
    )
    task = plan_evidence_followup(result)
    assert task.source_state == "evidence_attested"
    assert task.task_type == REVIEWER_VALIDATION_TASK
    assert task.owner_hint == "evidence_reviewer"
    assert task.required is True
    assert task.blocks_validation is True


def test_expired_evidence_creates_refresh_task() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
            expired=True,
        )
    )
    task = plan_evidence_followup(result)
    assert task.source_state == "evidence_expired"
    assert task.task_type == EVIDENCE_REFRESH_TASK
    assert task.required is True
    assert task.blocks_validation is True


def test_rejected_evidence_creates_corrective_task() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
            rejected=True,
        )
    )
    task = plan_evidence_followup(result)
    assert task.source_state == "evidence_rejected"
    assert task.task_type == CORRECTIVE_EVIDENCE_TASK
    assert task.required is True
    assert task.blocks_validation is True


def test_conflicting_evidence_creates_audit_review_and_human_review() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
            conflicting=True,
        )
    )
    task = plan_evidence_followup(result)
    assert task.source_state == "evidence_conflicting"
    assert task.task_type == AUDIT_REVIEW_TASK
    assert task.required is True
    assert task.blocks_validation is True
    assert task.human_review_required is True


def test_validated_evidence_creates_no_followup() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
            attested_by_owner=True,
            validated_by_reviewer=True,
            source="internal_repo",
            owner="control-owner",
            scope="ecc-1",
            control_binding="ecc.control.1",
            freshness="2026-q3",
        )
    )
    task = plan_evidence_followup(result)
    assert task.source_state == "evidence_validated"
    assert task.task_type == NO_FOLLOWUP_REQUIRED
    assert task.required is False
    assert task.blocks_validation is False
    assert task.human_review_required is False


def test_followup_does_not_emit_compliance_or_action_allowed() -> None:
    result = evaluate_evidence_maturity(EvidenceMaturityContext())
    task = plan_evidence_followup(result)
    payload = asdict(task)
    serialized = str(payload).lower()
    assert "compliant" not in serialized
    assert "compliance_status" not in serialized
    assert "action_allowed" not in serialized


def test_followup_preserves_missing_trace_fields_as_required_inputs() -> None:
    result = evaluate_evidence_maturity(EvidenceMaturityContext())
    task = plan_evidence_followup(result)
    assert task.source_state == "evidence_missing"
    assert set(task.required_inputs) == {"source", "owner", "scope", "control_binding", "freshness"}


def test_no_nca_approved_or_certified_wording() -> None:
    root = Path(__file__).resolve().parents[2]
    targets = [
        root / "governance_constitution" / "evidence_followup.py",
        root.parent / "docs" / "EVIDENCE_FOLLOWUP_TASKS.md",
    ]
    forbidden = ("certified by nca", "approved by nca", "nca certified", "nca approved")
    for target in targets:
        text = target.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            assert phrase not in text
