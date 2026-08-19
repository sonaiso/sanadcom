from __future__ import annotations

from governance_constitution.medical_policy import (
    load_medical_branch_policy,
    load_medical_branch_schema,
    validate_medical_branch_document,
)


def _valid_document() -> dict[str, object]:
    return {
        "document_type": "LicensedBranchConstitution",
        "document_id": "MED-LB-LUNG-RESECTION-001",
        "version": "1.0.0",
        "branch_license": {
            "license_id": "BL-MED-ONC-SURG-001",
            "origin": "Reality: patient body and lung tumor finding",
            "branch": "lung tumor surgical decision",
            "effective_attribute": ["tumor size", "tumor location", "histology type"],
            "sabab": "radiology finding for suspected malignant lesion",
            "conditions": [
                "histology confirmed",
                "staging completed",
                "surgical fitness completed"
            ],
            "blockers_mani": ["targeted therapy-first evidence is stronger"],
            "qadih_differences": ["biomarker-response evidence is not surgery-benefit evidence"],
            "evidence_requirements": {
                "trace_fields": [
                    "trace_id",
                    "source_type",
                    "scope",
                    "owner",
                    "freshness",
                    "control_binding",
                    "claim_link",
                    "relation_link"
                ],
                "minimum_set": [
                    "recent imaging",
                    "histology report",
                    "staging report",
                    "surgery-benefit evidence"
                ]
            },
            "rank_policy": {"action_threshold_rank": "SUPPORTED"},
            "residual_policy": [
                "record all failed gates",
                "never suppress exceptions as compliance"
            ]
        },
        "decision_object": {
            "decision_id": "DEC-MED-LUNG-001",
            "origin": "Reality: lung tumor",
            "branch": "lung tumor surgical decision",
            "branch_license_ref": "BL-MED-ONC-SURG-001",
            "effective_attribute": ["tumor size", "tumor location", "histology type"],
            "sabab": "need treatment decision",
            "evaluated_conditions": {
                "histology_confirmed": True,
                "staging_completed": True,
                "surgical_fitness_completed": True
            },
            "mani_blockers": ["targeted therapy-first evidence is stronger"],
            "qadih_differences": ["no direct surgery-benefit link from biomarker"],
            "evidence_trace_evaluation": {
                "claim": "immediate surgery is required",
                "relation_tested": "biomarker -> benefit_from_resection",
                "result": "UNPROVEN",
                "weakest_binding_rank": "CANDIDATE"
            },
            "rank": "CANDIDATE",
            "failed_stage": "EVIDENCE_TRACE",
            "residuals": ["no direct evidence for immediate surgery under biomarker X"],
            "handoff_delivery_decision": {
                "handoff_to": "multidisciplinary oncology team",
                "delivery_decision": "DEFERRED_ACTION",
                "action_allowed": False,
                "licensed_action": "targeted therapy with follow-up",
                "blocked_action": "immediate resection"
            }
        }
    }


def test_medical_schema_and_policy_files_are_loadable() -> None:
    schema = load_medical_branch_schema()
    policy = load_medical_branch_policy()
    assert schema["title"] == "Medical Licensed Branch Constitutional Document"
    assert policy["policy_id"] == "MED-LUNG-CONSTITUTION-POLICY-001"


def test_valid_medical_document_passes_schema_and_policy() -> None:
    violations = validate_medical_branch_document(_valid_document())
    assert violations == []


def test_missing_required_decision_fields_fail_schema_validation() -> None:
    document = _valid_document()
    del document["decision_object"]["branch_license_ref"]  # type: ignore[index]
    violations = validate_medical_branch_document(document)
    assert any("schema:decision_object" in item for item in violations)


def test_action_allowed_true_with_blockers_fails_policy() -> None:
    document = _valid_document()
    document["decision_object"]["handoff_delivery_decision"]["delivery_decision"] = "ALLOWED_ACTION"  # type: ignore[index]
    document["decision_object"]["handoff_delivery_decision"]["action_allowed"] = True  # type: ignore[index]
    document["decision_object"]["failed_stage"] = None  # type: ignore[index]
    document["decision_object"]["residuals"] = []  # type: ignore[index]
    violations = validate_medical_branch_document(document)
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
    violations = validate_medical_branch_document(document)
    assert "policy:rank below action threshold cannot produce action_allowed=true" in violations


def test_non_allowed_decision_requires_failed_stage_and_residuals() -> None:
    document = _valid_document()
    document["decision_object"]["failed_stage"] = None  # type: ignore[index]
    document["decision_object"]["residuals"] = []  # type: ignore[index]
    violations = validate_medical_branch_document(document)
    assert any("schema:decision_object.failed_stage" in item for item in violations)
    assert any("schema:decision_object.residuals" in item for item in violations)


def test_rank_must_not_exceed_weakest_binding() -> None:
    document = _valid_document()
    document["decision_object"]["rank"] = "SUPPORTED"  # type: ignore[index]
    document["decision_object"]["evidence_trace_evaluation"]["weakest_binding_rank"] = "CANDIDATE"  # type: ignore[index]
    violations = validate_medical_branch_document(document)
    assert "policy:rank exceeds weakest evidence binding rank" in violations
