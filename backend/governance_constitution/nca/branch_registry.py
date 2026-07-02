from governance_constitution.contracts import (
    BranchLicense,
    Condition,
    EffectiveAttribute,
    Mani,
    OriginNode,
    QadihDifference,
    RankPolicy,
    Sabab,
)
from governance_constitution.enums import EvidenceRank

ECC_ORIGIN = OriginNode("ECC", title="Essential Cybersecurity Controls")

NCA_BRANCH_LICENSES: dict[str, BranchLicense] = {
    "DCC": BranchLicense(
        origin=ECC_ORIGIN,
        branch_id="DCC",
        branch="DCC",
        effective_attribute=EffectiveAttribute("data_asset_lifecycle"),
        sabab=Sabab("organizational data assets exist"),
        conditions=(
            Condition("data_asset_scope_defined"),
            Condition("data_classification_declared"),
            Condition("data_owner_assigned"),
        ),
        mani=(
            Mani("no_data_assets_in_scope"),
            Mani("missing_data_classification"),
            Mani("missing_data_owner"),
        ),
        qadih_differences=(
            QadihDifference("asset_is_not_data_asset"),
            QadihDifference("policy_only_without_runtime_data_trace"),
        ),
        evidence_requirements=("source", "scope", "owner", "freshness", "control_binding"),
        rank_policy=RankPolicy(minimum_action_rank=EvidenceRank.SUPPORTED),
        residual_policy="record_all_failures",
    ),
    "CCC": BranchLicense(
        origin=ECC_ORIGIN,
        branch_id="CCC",
        branch="CCC",
        effective_attribute=EffectiveAttribute("cloud_service_security_scope"),
        sabab=Sabab("cloud services exist in organizational scope"),
        conditions=(
            Condition("cloud_scope_defined"),
            Condition("cloud_asset_inventory_exists"),
            Condition("cloud_shared_responsibility_defined"),
        ),
        mani=(
            Mani("no_cloud_scope"),
            Mani("missing_cloud_inventory"),
            Mani("missing_shared_responsibility_matrix"),
        ),
        qadih_differences=(
            QadihDifference("service_is_not_cloud_service"),
            QadihDifference("policy_only_without_runtime_cloud_trace"),
        ),
        evidence_requirements=("source", "scope", "owner", "freshness", "control_binding"),
        rank_policy=RankPolicy(minimum_action_rank=EvidenceRank.SUPPORTED),
        residual_policy="record_all_failures",
    ),
    "CSCC": BranchLicense(
        origin=ECC_ORIGIN,
        branch_id="CSCC",
        branch="CSCC",
        effective_attribute=EffectiveAttribute("critical_system_assurance"),
        sabab=Sabab("critical systems are designated in scope"),
        conditions=(
            Condition("critical_system_scope_defined"),
            Condition("criticality_designation_approved"),
            Condition("system_boundary_defined"),
        ),
        mani=(
            Mani("no_critical_systems_in_scope"),
            Mani("criticality_not_designated"),
            Mani("system_boundary_missing"),
        ),
        qadih_differences=(
            QadihDifference("system_not_designated_critical"),
            QadihDifference("system_classification_conflict"),
        ),
        evidence_requirements=("source", "scope", "owner", "freshness", "control_binding"),
        rank_policy=RankPolicy(minimum_action_rank=EvidenceRank.SUPPORTED),
        residual_policy="record_all_failures",
    ),
    "OTCC": BranchLicense(
        origin=ECC_ORIGIN,
        branch_id="OTCC",
        branch="OTCC",
        effective_attribute=EffectiveAttribute("ot_ics_security_boundary"),
        sabab=Sabab("OT or ICS assets exist in scope"),
        conditions=(
            Condition("ot_scope_defined"),
            Condition("ot_asset_inventory_exists"),
            Condition("ot_facility_level_declared"),
        ),
        mani=(
            Mani("no_ot_ics_assets_in_scope"),
            Mani("missing_ot_inventory"),
            Mani("missing_ot_facility_level"),
        ),
        qadih_differences=(
            QadihDifference("asset_is_not_ot_ics_asset"),
            QadihDifference("it_policy_substitutes_ot_control"),
        ),
        evidence_requirements=("source", "scope", "owner", "freshness", "control_binding"),
        rank_policy=RankPolicy(minimum_action_rank=EvidenceRank.SUPPORTED),
        residual_policy="record_all_failures",
    ),
    "TCC": BranchLicense(
        origin=ECC_ORIGIN,
        branch_id="TCC",
        branch="TCC",
        effective_attribute=EffectiveAttribute("remote_work_access_security"),
        sabab=Sabab("remote work or remote access exists in scope"),
        conditions=(
            Condition("remote_scope_defined"),
            Condition("remote_access_policy_exists"),
            Condition("remote_mfa_required"),
        ),
        mani=(
            Mani("no_remote_scope"),
            Mani("missing_remote_access_policy"),
            Mani("missing_remote_mfa"),
        ),
        qadih_differences=(
            QadihDifference("vpn_only_without_remote_security_scope"),
            QadihDifference("remote_access_outside_governed_scope"),
        ),
        evidence_requirements=("source", "scope", "owner", "freshness", "control_binding"),
        rank_policy=RankPolicy(minimum_action_rank=EvidenceRank.SUPPORTED),
        residual_policy="record_all_failures",
    ),
}
