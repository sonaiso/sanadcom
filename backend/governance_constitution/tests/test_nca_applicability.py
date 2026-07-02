from dataclasses import asdict
from pathlib import Path

from governance_constitution.nca.applicability import (
    NCAApplicabilityContext,
    evaluate_nca_applicability,
)


def _result_for(
    context: NCAApplicabilityContext,
    branch_id: str,
):
    return next(result for result in evaluate_nca_applicability(context) if result.branch_id == branch_id)


def test_dcc_applicable_when_data_scope_conditions_exist() -> None:
    result = _result_for(
        NCAApplicabilityContext(
            has_data_assets=True,
            data_asset_scope_defined=True,
            data_classification_declared=True,
            data_owner_assigned=True,
        ),
        "DCC",
    )
    assert result.applicable is True
    assert result.blocked is False
    assert result.state == "branch_applicable"


def test_dcc_blocked_without_data_assets() -> None:
    result = _result_for(NCAApplicabilityContext(), "DCC")
    assert result.applicable is False
    assert result.blocked is True
    assert "no_data_assets_in_scope" in result.active_mani
    assert result.state == "branch_blocked"


def test_dcc_deferred_without_classification() -> None:
    result = _result_for(
        NCAApplicabilityContext(
            has_data_assets=True,
            data_asset_scope_defined=True,
            data_owner_assigned=True,
        ),
        "DCC",
    )
    assert result.applicable is False
    assert result.blocked is False
    assert "data_classification_declared" in result.missing_conditions
    assert result.state == "branch_candidate"


def test_ccc_applicable_when_cloud_scope_and_shared_responsibility_exist() -> None:
    result = _result_for(
        NCAApplicabilityContext(
            has_cloud_services=True,
            cloud_scope_defined=True,
            cloud_asset_inventory_exists=True,
            cloud_shared_responsibility_defined=True,
        ),
        "CCC",
    )
    assert result.applicable is True
    assert result.blocked is False
    assert result.state == "branch_applicable"


def test_ccc_blocked_without_cloud_scope() -> None:
    result = _result_for(NCAApplicabilityContext(), "CCC")
    assert result.applicable is False
    assert result.blocked is True
    assert "no_cloud_scope" in result.active_mani
    assert result.state == "branch_blocked"


def test_cscc_blocked_without_criticality_designation() -> None:
    result = _result_for(
        NCAApplicabilityContext(
            has_critical_systems=True,
            critical_system_scope_defined=True,
            system_boundary_defined=True,
            criticality_designation_approved=False,
        ),
        "CSCC",
    )
    assert result.applicable is False
    assert result.blocked is True
    assert "criticality_not_designated" in result.active_mani
    assert "system_not_designated_critical" in result.qadih_differences
    assert result.state == "branch_blocked"


def test_otcc_blocked_for_pure_it_scope() -> None:
    result = _result_for(
        NCAApplicabilityContext(
            has_data_assets=True,
            has_cloud_services=True,
            has_ot_ics_assets=False,
        ),
        "OTCC",
    )
    assert result.applicable is False
    assert result.blocked is True
    assert "no_ot_ics_assets_in_scope" in result.active_mani
    assert "asset_is_not_ot_ics_asset" in result.qadih_differences
    assert result.state == "branch_blocked"


def test_tcc_applicable_for_remote_work_with_policy_and_mfa() -> None:
    result = _result_for(
        NCAApplicabilityContext(
            has_remote_work=True,
            remote_scope_defined=True,
            remote_access_policy_exists=True,
            remote_mfa_required=True,
        ),
        "TCC",
    )
    assert result.applicable is True
    assert result.blocked is False
    assert result.state == "branch_applicable"


def test_applicability_does_not_emit_compliance_decision() -> None:
    result = _result_for(NCAApplicabilityContext(), "DCC")
    payload = asdict(result)
    serialized = str(payload).lower()
    assert "compliant" not in serialized
    assert "certified" not in serialized
    assert "approved" not in serialized
    assert "action_allowed" not in payload


def test_no_nca_certified_or_approved_wording() -> None:
    root = Path(__file__).resolve().parents[2]
    targets = [
        root / "governance_constitution" / "nca" / "branch_registry.py",
        root / "governance_constitution" / "nca" / "applicability.py",
        root.parents[0] / "docs" / "NCA_APPLICABILITY_ENGINE.md",
    ]
    forbidden = ("certified by nca", "approved by nca", "nca certified", "nca approved")
    for target in targets:
        text = target.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            assert phrase not in text
