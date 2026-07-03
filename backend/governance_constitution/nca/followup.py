from dataclasses import dataclass

from .applicability import NCAApplicabilityResult

NO_FOLLOWUP_REQUIRED = "no_followup_required"
SCOPING_REQUEST = "scoping_request"
SCOPE_CONFLICT_REVIEW = "scope_conflict_review"


_SCOPING_OWNER_BY_BRANCH: dict[str, str] = {
    "DCC": "data_owner",
    "CCC": "cloud_security_owner",
    "CSCC": "system_owner",
    "OTCC": "ot_security_owner",
    "TCC": "remote_access_owner",
}

_CONFLICT_OWNER_BY_BRANCH: dict[str, str] = {
    "DCC": "cybersecurity_governance",
    "CCC": "cloud_security_owner",
    "CSCC": "cybersecurity_governance",
    "OTCC": "ot_security_owner",
    "TCC": "cybersecurity_governance",
}


@dataclass(frozen=True)
class NCAApplicabilityFollowupTask:
    branch_id: str
    source_state: str
    task_type: str
    required: bool
    owner_role: str | None
    reason_codes: tuple[str, ...]
    required_inputs: tuple[str, ...]
    audit_notes: tuple[str, ...]
    blocks_validation: bool
    human_review_required: bool


def _owner_role_for_branch(branch_id: str, mapping: dict[str, str]) -> str:
    try:
        return mapping[branch_id]
    except KeyError as exc:
        raise ValueError(f"unknown branch id: {branch_id}") from exc


def plan_nca_branch_followup(result: NCAApplicabilityResult) -> NCAApplicabilityFollowupTask:
    if result.state == "branch_out_of_scope":
        return NCAApplicabilityFollowupTask(
            branch_id=result.branch_id,
            source_state=result.state,
            task_type=NO_FOLLOWUP_REQUIRED,
            required=False,
            owner_role=None,
            reason_codes=(),
            required_inputs=(),
            audit_notes=result.qadih_differences,
            blocks_validation=False,
            human_review_required=False,
        )

    if result.state == "branch_in_scope":
        return NCAApplicabilityFollowupTask(
            branch_id=result.branch_id,
            source_state=result.state,
            task_type=NO_FOLLOWUP_REQUIRED,
            required=False,
            owner_role=None,
            reason_codes=(),
            required_inputs=(),
            audit_notes=(),
            blocks_validation=False,
            human_review_required=False,
        )

    if result.state == "branch_needs_scoping":
        owner_role = _owner_role_for_branch(result.branch_id, _SCOPING_OWNER_BY_BRANCH)
        return NCAApplicabilityFollowupTask(
            branch_id=result.branch_id,
            source_state=result.state,
            task_type=SCOPING_REQUEST,
            required=True,
            owner_role=owner_role,
            reason_codes=result.missing_conditions,
            required_inputs=result.missing_conditions,
            audit_notes=result.qadih_differences,
            blocks_validation=True,
            human_review_required=False,
        )

    if result.state == "branch_scope_conflict":
        owner_role = _owner_role_for_branch(result.branch_id, _CONFLICT_OWNER_BY_BRANCH)
        reason_codes = result.active_mani + result.qadih_differences
        return NCAApplicabilityFollowupTask(
            branch_id=result.branch_id,
            source_state=result.state,
            task_type=SCOPE_CONFLICT_REVIEW,
            required=True,
            owner_role=owner_role,
            reason_codes=reason_codes,
            required_inputs=(),
            audit_notes=result.qadih_differences,
            blocks_validation=True,
            human_review_required=True,
        )

    raise ValueError(f"unknown applicability state: {result.state}")


def plan_nca_applicability_followups(
    results: tuple[NCAApplicabilityResult, ...],
) -> tuple[NCAApplicabilityFollowupTask, ...]:
    return tuple(plan_nca_branch_followup(result) for result in results)
