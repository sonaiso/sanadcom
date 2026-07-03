from dataclasses import asdict
from pathlib import Path

from governance_constitution.evidence_maturity import (
    EVIDENCE_ATTESTED,
    EVIDENCE_CONFLICTING,
    EVIDENCE_DRAFT,
    EVIDENCE_EXPIRED,
    EVIDENCE_MISSING,
    EVIDENCE_SUBMITTED,
    EVIDENCE_VALIDATED,
    EvidenceMaturityContext,
    evaluate_evidence_maturity,
)


def test_missing_evidence_state() -> None:
    result = evaluate_evidence_maturity(EvidenceMaturityContext())
    assert result.state == EVIDENCE_MISSING
    assert result.required is True
    assert result.blocks_validation is True


def test_draft_evidence_state() -> None:
    result = evaluate_evidence_maturity(EvidenceMaturityContext(evidence_refs=("ev-1",)))
    assert result.state == EVIDENCE_DRAFT
    assert result.required is True
    assert result.blocks_validation is True


def test_submitted_without_attestation() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
        )
    )
    assert result.state == EVIDENCE_SUBMITTED
    assert result.required is True
    assert "owner_attestation_pending" in result.reason_codes


def test_attested_without_validation() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
            attested_by_owner=True,
        )
    )
    assert result.state == EVIDENCE_ATTESTED
    assert result.required is True
    assert "reviewer_validation_pending" in result.reason_codes


def test_validated_evidence_is_not_compliance() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
            attested_by_owner=True,
            validated_by_reviewer=True,
        )
    )
    payload = asdict(result)
    serialized = str(payload).lower()
    assert result.state == EVIDENCE_VALIDATED
    assert "internal_validation_only_not_compliance_decision" in result.audit_notes
    assert "compliant" not in serialized
    assert "compliance_status" not in serialized


def test_expired_evidence_blocks_validation() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
            expired=True,
        )
    )
    assert result.state == EVIDENCE_EXPIRED
    assert result.blocks_validation is True


def test_conflicting_evidence_requires_human_review() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
            conflicting=True,
        )
    )
    assert result.state == EVIDENCE_CONFLICTING
    assert result.human_review_required is True


def test_missing_trace_fields_are_reported() -> None:
    result = evaluate_evidence_maturity(
        EvidenceMaturityContext(
            evidence_refs=("ev-1",),
            submitted=True,
        )
    )
    assert set(result.missing_fields) == {"owner", "scope", "control_binding", "freshness"}
    assert set(result.audit_notes) >= {
        "missing_trace_field:owner",
        "missing_trace_field:scope",
        "missing_trace_field:control_binding",
        "missing_trace_field:freshness",
    }


def test_no_action_allowed_or_compliant_wording() -> None:
    result = evaluate_evidence_maturity(EvidenceMaturityContext())
    payload = asdict(result)
    serialized = str(payload).lower()
    assert "action_allowed" not in serialized
    assert "compliant" not in serialized


def test_no_nca_approved_or_certified_wording() -> None:
    root = Path(__file__).resolve().parents[2]
    targets = [
        root / "governance_constitution" / "evidence_maturity.py",
        root.parent / "docs" / "EVIDENCE_MATURITY_MODEL.md",
    ]
    forbidden = ("certified by nca", "approved by nca", "nca certified", "nca approved")
    for target in targets:
        text = target.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            assert phrase not in text
