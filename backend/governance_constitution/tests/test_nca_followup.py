from dataclasses import asdict
from pathlib import Path

import pytest

from governance_constitution.nca.applicability import (
    NCAApplicabilityContext,
    NCAApplicabilityResult,
    evaluate_nca_applicability,
)
from governance_constitution.nca.followup import (
    NO_FOLLOWUP_REQUIRED,
    SCOPING_REQUEST,
    SCOPE_CONFLICT_REVIEW,
    plan_nca_applicability_followups,
    plan_nca_branch_followup,
)


def _result_for(context: NCAApplicabilityContext, branch_id: str) -> NCAApplicabilityResult:
    return next(result for result in evaluate_nca_applicability(context) if result.branch_id == branch_id)


def test_out_of_scope_creates_no_required_followup() -> None:
    task = plan_nca_branch_followup(_result_for(NCAApplicabilityContext(), "DCC"))
    assert task.source_state == "branch_out_of_scope"
    assert task.task_type == NO_FOLLOWUP_REQUIRED
    assert task.required is False
    assert task.blocks_validation is False
    assert task.human_review_required is False
    assert task.required_inputs == ()


def test_out_of_scope_qadih_is_audit_note_only_not_human_review() -> None:
    task = plan_nca_branch_followup(
        _result_for(
            NCAApplicabilityContext(has_data_assets=True, has_cloud_services=True, has_ot_ics_assets=False),
            "OTCC",
        )
    )
    assert task.source_state == "branch_out_of_scope"
    assert "asset_is_not_ot_ics_asset" in task.audit_notes
    assert task.human_review_required is False
    assert task.required is False


def test_in_scope_creates_no_required_followup() -> None:
    task = plan_nca_branch_followup(
        _result_for(
            NCAApplicabilityContext(
                has_data_assets=True,
                data_asset_scope_defined=True,
                data_classification_declared=True,
                data_owner_assigned=True,
            ),
            "DCC",
        )
    )
    assert task.source_state == "branch_in_scope"
    assert task.task_type == NO_FOLLOWUP_REQUIRED
    assert task.required is False
    assert task.blocks_validation is False
    assert task.human_review_required is False
    assert task.reason_codes == ()
    assert task.required_inputs == ()


def test_needs_scoping_creates_scoping_request_with_required_inputs() -> None:
    task = plan_nca_branch_followup(
        _result_for(
            NCAApplicabilityContext(
                has_data_assets=True,
                data_asset_scope_defined=True,
                data_owner_assigned=True,
            ),
            "DCC",
        )
    )
    assert task.source_state == "branch_needs_scoping"
    assert task.task_type == SCOPING_REQUEST
    assert task.required is True
    assert task.blocks_validation is True
    assert task.human_review_required is False
    assert task.owner_role == "data_owner"
    assert task.required_inputs == ("data_classification_declared",)
    assert task.reason_codes == ("data_classification_declared",)


def test_ccc_needs_shared_responsibility_routes_to_cloud_owner() -> None:
    task = plan_nca_branch_followup(
        _result_for(
            NCAApplicabilityContext(
                has_cloud_services=True,
                cloud_scope_defined=True,
                cloud_asset_inventory_exists=True,
            ),
            "CCC",
        )
    )
    assert task.source_state == "branch_needs_scoping"
    assert task.task_type == SCOPING_REQUEST
    assert task.owner_role == "cloud_security_owner"
    assert "cloud_shared_responsibility_defined" in task.reason_codes


def test_cscc_scope_conflict_creates_human_review_task() -> None:
    task = plan_nca_branch_followup(
        _result_for(
            NCAApplicabilityContext(
                has_critical_systems=True,
                critical_system_scope_defined=True,
                system_boundary_defined=True,
                criticality_designation_approved=False,
            ),
            "CSCC",
        )
    )
    assert task.source_state == "branch_scope_conflict"
    assert task.task_type == SCOPE_CONFLICT_REVIEW
    assert task.required is True
    assert task.human_review_required is True
    assert task.owner_role == "cybersecurity_governance"
    assert "criticality_not_designated" in task.reason_codes
    assert "system_not_designated_critical" in task.reason_codes
    assert "system_not_designated_critical" in task.audit_notes


def test_scope_conflict_blocks_validation() -> None:
    task = plan_nca_branch_followup(
        _result_for(
            NCAApplicabilityContext(
                has_critical_systems=True,
                critical_system_scope_defined=True,
                system_boundary_defined=True,
            ),
            "CSCC",
        )
    )
    assert task.source_state == "branch_scope_conflict"
    assert task.blocks_validation is True


def test_unknown_state_rejected() -> None:
    with pytest.raises(ValueError, match="unknown applicability state"):
        plan_nca_branch_followup(
            NCAApplicabilityResult(
                branch_id="DCC",
                state="branch_unknown_state",
                applicable=False,
                blocked=False,
                missing_conditions=(),
                active_mani=(),
                qadih_differences=(),
                branch_license=None,
            )
        )


def test_followup_does_not_emit_compliance_decision_or_action_allowed() -> None:
    results = evaluate_nca_applicability(NCAApplicabilityContext())
    tasks = plan_nca_applicability_followups(results)
    payload = [asdict(task) for task in tasks]
    serialized = str(payload).lower()
    assert "compliant" not in serialized
    assert "certified" not in serialized
    assert "approved" not in serialized
    assert "action_allowed" not in serialized


def test_no_nca_certified_or_approved_wording() -> None:
    root = Path(__file__).resolve().parents[2]
    targets = [
        root / "governance_constitution" / "nca" / "followup.py",
        root.parent / "docs" / "NCA_APPLICABILITY_FOLLOWUP_TASKS.md",
    ]
    forbidden = ("certified by nca", "approved by nca", "nca certified", "nca approved")
    for target in targets:
        text = target.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            assert phrase not in text
