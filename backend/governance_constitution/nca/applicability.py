from dataclasses import dataclass

from governance_constitution.contracts import BranchLicense
from governance_constitution.enums import BranchApplicabilityState

from .branch_registry import NCA_BRANCH_LICENSES


@dataclass(frozen=True)
class NCAApplicabilityContext:
    has_data_assets: bool = False
    has_cloud_services: bool = False
    has_critical_systems: bool = False
    has_ot_ics_assets: bool = False
    has_remote_work: bool = False
    has_remote_access: bool = False

    data_asset_scope_defined: bool = False
    data_classification_declared: bool = False
    data_owner_assigned: bool = False

    cloud_scope_defined: bool = False
    cloud_shared_responsibility_defined: bool = False
    cloud_asset_inventory_exists: bool = False

    critical_system_scope_defined: bool = False
    criticality_designation_approved: bool = False
    system_boundary_defined: bool = False
    criticality_designation_rejected: bool = False
    system_boundary_conflict: bool = False
    system_classification_conflict: bool = False

    ot_scope_defined: bool = False
    ot_asset_inventory_exists: bool = False
    ot_facility_level_declared: bool = False

    remote_scope_defined: bool = False
    remote_access_policy_exists: bool = False
    remote_mfa_required: bool = False


@dataclass(frozen=True)
class NCAApplicabilityResult:
    branch_id: str
    state: BranchApplicabilityState
    applicable: bool
    blocked: bool
    missing_conditions: tuple[str, ...]
    active_mani: tuple[str, ...]
    qadih_differences: tuple[str, ...]
    branch_license: BranchLicense | None


def _scope_available(branch_id: str, context: NCAApplicabilityContext) -> bool:
    return {
        "DCC": context.has_data_assets,
        "CCC": context.has_cloud_services,
        "CSCC": context.has_critical_systems,
        "OTCC": context.has_ot_ics_assets,
        "TCC": context.has_remote_work or context.has_remote_access,
    }[branch_id]


def _condition_state(context: NCAApplicabilityContext) -> dict[str, bool]:
    return {
        "data_asset_scope_defined": context.data_asset_scope_defined,
        "data_classification_declared": context.data_classification_declared,
        "data_owner_assigned": context.data_owner_assigned,
        "cloud_scope_defined": context.cloud_scope_defined,
        "cloud_asset_inventory_exists": context.cloud_asset_inventory_exists,
        "cloud_shared_responsibility_defined": context.cloud_shared_responsibility_defined,
        "critical_system_scope_defined": context.critical_system_scope_defined,
        "criticality_designation_approved": context.criticality_designation_approved,
        "system_boundary_defined": context.system_boundary_defined,
        "ot_scope_defined": context.ot_scope_defined,
        "ot_asset_inventory_exists": context.ot_asset_inventory_exists,
        "ot_facility_level_declared": context.ot_facility_level_declared,
        "remote_scope_defined": context.remote_scope_defined,
        "remote_access_policy_exists": context.remote_access_policy_exists,
        "remote_mfa_required": context.remote_mfa_required,
    }


def _active_mani(branch_id: str, context: NCAApplicabilityContext) -> tuple[str, ...]:
    if not _scope_available(branch_id, context):
        return ()
    if branch_id == "CSCC":
        blockers: list[str] = []
        if context.criticality_designation_rejected:
            blockers.append("criticality_designation_rejected")
        if context.system_boundary_conflict:
            blockers.append("system_boundary_conflict")
        if context.system_classification_conflict:
            blockers.append("system_classification_conflict")
        return tuple(blockers)
    return ()


def _qadih_differences(branch_id: str, context: NCAApplicabilityContext) -> tuple[str, ...]:
    has_non_data_assets = context.has_cloud_services or context.has_ot_ics_assets or context.has_critical_systems
    has_non_cloud_assets = context.has_data_assets or context.has_ot_ics_assets

    if branch_id == "DCC" and not context.has_data_assets and has_non_data_assets:
        return ("asset_is_not_data_asset",)
    if branch_id == "CCC" and not context.has_cloud_services and has_non_cloud_assets:
        return ("service_is_not_cloud_service",)
    if branch_id == "CSCC" and context.has_critical_systems and not context.criticality_designation_approved:
        return ("system_not_designated_critical",)
    if branch_id == "OTCC" and not context.has_ot_ics_assets and (
        context.has_data_assets or context.has_cloud_services
    ):
        return ("asset_is_not_ot_ics_asset",)
    if branch_id == "TCC" and (context.has_remote_work or context.has_remote_access) and not context.remote_scope_defined:
        return ("remote_access_outside_governed_scope",)
    return ()


def _evaluate_branch_applicability(
    *,
    branch_id: str,
    branch_license: BranchLicense,
    context: NCAApplicabilityContext,
    states: dict[str, bool],
) -> NCAApplicabilityResult:
    in_scope = _scope_available(branch_id, context)
    active_mani = _active_mani(branch_id, context)
    qadih_differences = _qadih_differences(branch_id, context)

    if not in_scope and not active_mani:
        return NCAApplicabilityResult(
            branch_id=branch_id,
            state=BranchApplicabilityState.NOT_APPLICABLE,
            applicable=False,
            blocked=False,
            missing_conditions=(),
            active_mani=(),
            qadih_differences=qadih_differences,
            branch_license=branch_license,
        )

    missing_conditions = tuple(
        condition.condition_id for condition in branch_license.conditions if not states.get(condition.condition_id, False)
    )

    blocked = bool(active_mani)
    applicable = in_scope and not blocked and not missing_conditions
    state = BranchApplicabilityState.APPLICABLE
    if blocked:
        state = BranchApplicabilityState.BLOCKED
    elif missing_conditions:
        state = BranchApplicabilityState.CANDIDATE

    return NCAApplicabilityResult(
        branch_id=branch_id,
        state=state,
        applicable=applicable,
        blocked=blocked,
        missing_conditions=missing_conditions,
        active_mani=active_mani,
        qadih_differences=qadih_differences,
        branch_license=branch_license,
    )


def evaluate_nca_applicability(context: NCAApplicabilityContext) -> tuple[NCAApplicabilityResult, ...]:
    states = _condition_state(context)
    results: list[NCAApplicabilityResult] = []

    for branch_id, branch_license in NCA_BRANCH_LICENSES.items():
        results.append(
            _evaluate_branch_applicability(
                branch_id=branch_id,
                branch_license=branch_license,
                context=context,
                states=states,
            )
        )

    return tuple(results)
