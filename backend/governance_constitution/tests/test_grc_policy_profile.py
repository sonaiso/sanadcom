from __future__ import annotations

from governance_constitution.grc_policy_profile import (
    load_grc_branch_policy,
    load_grc_branch_schema,
    validate_grc_branch_document,
)


def _valid_document() -> dict[str, object]:
    return {
        "document_type": "LicensedBranchConstitution",
        "document_id": "GRC-LB-DCC-001",
        "version": "1.0.0",
        "branch_license": {
            "license_id": "BL-ECC-DCC-001",
            "origin": "ECC",
            "branch": "DCC-01 applicability for data governance control",
            "effective_attribute": [
                "critical data assets",
                "regulated business process",
                "in-scope production systems",
            ],
            "sabab": "regulated data processing under ECC-origin controls",
            "conditions": [
                "asset_inventory_completed",
                "control_owner_assigned",
                "implementation_evidence_collected",
            ],
            "blockers_mani": ["control owner attestation missing"],
            "qadih_differences": ["policy text exists without implementation proof"],
            "evidence_requirements": {
                "trace_fields": [
                    "trace_id",
                    "source_type",
                    "scope",
                    "owner",
                    "freshness",
                    "control_binding",
                    "claim_link",
                    "relation_link",
                ],
                "minimum_set": [
                    "signed control implementation record",
                    "audit sample evidence",
                    "system configuration proof",
                    "owner attestation",
                ],
            },
            "rank_policy": {"action_threshold_rank": "SUPPORTED"},
            "residual_policy": [
                "record all failed gates",
                "record exceptions explicitly as residuals",
            ],
        },
        "decision_object": {
            "decision_id": "DEC-GRC-DCC-001",
            "origin": "ECC",
            "branch": "DCC-01 applicability for data governance control",
            "branch_license_ref": "BL-ECC-DCC-001",
            "effective_attribute": [
                "critical data assets",
                "regulated business process",
                "in-scope production systems",
            ],
            "sabab": "assessment requires governed decision",
            "evaluated_conditions": {
                "asset_inventory_completed": True,
                "control_owner_assigned": True,
                "implementation_evidence_collected": True,
            },
            "mani_blockers": ["control owner attestation missing"],
            "qadih_differences": ["policy-only evidence is not implementation proof"],
            "evidence_trace_evaluation": {
                "claim": "DCC-01 is verified and can be marked compliant",
                "relation_tested": "policy_attachment -> control_verified",
                "result": "UNPROVEN",
                "weakest_binding_rank": "CANDIDATE",
            },
            "rank": "CANDIDATE",
            "failed_stage": "EVIDENCE_TRACE",
            "residuals": ["missing direct implementation evidence for DCC-01"],
            "handoff_delivery_decision": {
                "handoff_to": "GRC and control-owner review queue",
                "delivery_decision": "DEFERRED_ACTION",
                "action_allowed": False,
                "licensed_action": "open evidence follow-up and remediation workflow",
                "blocked_action": "mark control verified and close compliance finding",
            },
        },
    }


def test_grc_schema_and_policy_files_are_loadable() -> None:
    schema = load_grc_branch_schema()
    policy = load_grc_branch_policy()
    assert schema["title"] == "GRC Cybersecurity Licensed Branch Constitutional Document"
    assert policy["policy_id"] == "GRC-CYBER-CONSTITUTION-POLICY-001"


def test_valid_grc_document_passes_schema_and_policy() -> None:
    violations = validate_grc_branch_document(_valid_document())
    assert violations == []


def test_missing_required_decision_fields_fail_schema_validation() -> None:
    document = _valid_document()
    del document["decision_object"]["branch_license_ref"]  # type: ignore[index]
    violations = validate_grc_branch_document(document)
    assert any("schema:decision_object" in item for item in violations)


def test_action_allowed_true_with_blockers_fails_policy() -> None:
    document = _valid_document()
    document["decision_object"]["handoff_delivery_decision"]["delivery_decision"] = "ALLOWED_ACTION"  # type: ignore[index]
    document["decision_object"]["handoff_delivery_decision"]["action_allowed"] = True  # type: ignore[index]
    document["decision_object"]["failed_stage"] = None  # type: ignore[index]
    document["decision_object"]["residuals"] = []  # type: ignore[index]
    violations = validate_grc_branch_document(document)
    assert "policy:action_allowed must be false when mani blockers exist" in violations


def test_rank_below_policy_threshold_cannot_allow_action() -> None:
    document = _valid_document()
    document["decision_object"]["mani_blockers"] = []  # type: ignore[index]
    document["decision_object"]["rank"] = "HYPOTHESIS"  # type: ignore[index]
    document["decision_object"]["evidence_trace_evaluation"]["weakest_binding_rank"] = "HYPOTHESIS"  # type: ignore[index]
    document["decision_object"]["handoff_delivery_decision"]["delivery_decision"] = "ALLOWED_ACTION"  # type: ignore[index]
    document["decision_object"]["handoff_delivery_decision"]["action_allowed"] = True  # type: ignore[index]
    document["decision_object"]["failed_stage"] = None  # type: ignore[index]
    document["decision_object"]["residuals"] = []  # type: ignore[index]
    violations = validate_grc_branch_document(document)
    assert "policy:rank below action threshold cannot produce action_allowed=true" in violations


def test_non_allowed_decision_requires_failed_stage_and_residuals() -> None:
    document = _valid_document()
    document["decision_object"]["failed_stage"] = None  # type: ignore[index]
    document["decision_object"]["residuals"] = []  # type: ignore[index]
    violations = validate_grc_branch_document(document)
    assert any("schema:decision_object.failed_stage" in item for item in violations)
    assert any("schema:decision_object.residuals" in item for item in violations)


def test_rank_must_not_exceed_weakest_binding() -> None:
    document = _valid_document()
    document["decision_object"]["rank"] = "SUPPORTED"  # type: ignore[index]
    document["decision_object"]["evidence_trace_evaluation"]["weakest_binding_rank"] = "CANDIDATE"  # type: ignore[index]
    violations = validate_grc_branch_document(document)
    assert "policy:rank exceeds weakest evidence binding rank" in violations
