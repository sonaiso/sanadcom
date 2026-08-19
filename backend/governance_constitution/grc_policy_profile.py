from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover - fallback exercised in CI environments without jsonschema.
    Draft202012Validator = None

RANK_ORDER = {
    "ZERO": 0,
    "CANDIDATE": 1,
    "HYPOTHESIS": 2,
    "SUPPORTED": 3,
    "VERIFIED": 4,
}

_BASE_DIR = Path(__file__).resolve().parent
_SCHEMA_PATH = _BASE_DIR / "schemas" / "grc_cybersecurity_licensed_branch.schema.json"
_POLICY_PATH = _BASE_DIR / "policies" / "grc_cybersecurity_licensed_branch_policy.json"


def load_grc_branch_schema() -> dict[str, Any]:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def load_grc_branch_policy() -> dict[str, Any]:
    return json.loads(_POLICY_PATH.read_text(encoding="utf-8"))


def _manual_schema_fallback_errors(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_root = (
        "document_type",
        "document_id",
        "version",
        "branch_license",
        "decision_object",
    )
    for key in required_root:
        if key not in document:
            errors.append(f"schema:<root>: missing required property '{key}'")
    if errors:
        return errors

    decision = document.get("decision_object")
    if not isinstance(decision, dict):
        return ["schema:decision_object: must be an object"]

    required_decision = (
        "decision_id",
        "origin",
        "branch",
        "branch_license_ref",
        "effective_attribute",
        "sabab",
        "evaluated_conditions",
        "mani_blockers",
        "qadih_differences",
        "evidence_trace_evaluation",
        "rank",
        "failed_stage",
        "residuals",
        "handoff_delivery_decision",
    )
    for key in required_decision:
        if key not in decision:
            errors.append(f"schema:decision_object: missing required property '{key}'")

    if errors:
        return errors

    handoff = decision.get("handoff_delivery_decision")
    if not isinstance(handoff, dict):
        return ["schema:decision_object.handoff_delivery_decision: must be an object"]

    delivery_decision = handoff.get("delivery_decision")
    if delivery_decision != "ALLOWED_ACTION":
        if decision.get("failed_stage") is None:
            errors.append(
                "schema:decision_object.failed_stage: failed_stage is required when delivery_decision is not ALLOWED_ACTION"
            )
        residuals = decision.get("residuals")
        if not isinstance(residuals, list) or len(residuals) == 0:
            errors.append(
                "schema:decision_object.residuals: residuals must contain at least one item when delivery_decision is not ALLOWED_ACTION"
            )

    return errors


def validate_grc_branch_document(document: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    schema = load_grc_branch_schema()
    policy = load_grc_branch_policy()

    if Draft202012Validator is not None:
        validator = Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
            path = ".".join(str(part) for part in error.path)
            location = path or "<root>"
            violations.append(f"schema:{location}: {error.message}")
    else:
        violations.extend(_manual_schema_fallback_errors(document))

    if violations:
        return violations

    decision = document["decision_object"]
    handoff = decision["handoff_delivery_decision"]
    delivery_decision = handoff["delivery_decision"]
    action_allowed = handoff["action_allowed"]
    rank = decision["rank"]
    weakest_binding_rank = decision["evidence_trace_evaluation"]["weakest_binding_rank"]

    if policy["enforce"]["no_action_with_active_mani"] and decision["mani_blockers"] and action_allowed:
        violations.append("policy:action_allowed must be false when mani blockers exist")

    if action_allowed and RANK_ORDER[rank] < RANK_ORDER[policy["action_threshold_rank"]]:
        violations.append("policy:rank below action threshold cannot produce action_allowed=true")

    if (
        policy["enforce"]["rank_must_not_exceed_weakest_binding"]
        and RANK_ORDER[rank] > RANK_ORDER[weakest_binding_rank]
    ):
        violations.append("policy:rank exceeds weakest evidence binding rank")

    if delivery_decision != "ALLOWED_ACTION":
        if policy["enforce"]["require_failed_stage_when_not_allowed"] and not decision["failed_stage"]:
            violations.append("policy:failed_stage is required when delivery_decision is not ALLOWED_ACTION")
        if policy["enforce"]["require_residuals_when_not_allowed"] and not decision["residuals"]:
            violations.append("policy:residuals are required when delivery_decision is not ALLOWED_ACTION")

    return violations
