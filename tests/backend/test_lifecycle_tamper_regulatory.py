"""
Tests for control lifecycle management, evidence tamper protection,
and regulatory version register.
"""

import pytest
from datetime import datetime, date


# ---------------------------------------------------------------------------
# Control lifecycle management
# ---------------------------------------------------------------------------

def test_control_lifecycle_status_enum():
    """ControlLifecycleStatus enum has all required states."""
    from controls.models import ControlLifecycleStatus

    required_states = {"draft", "reviewed", "approved", "published", "deprecated"}
    actual_values = {s.value for s in ControlLifecycleStatus}
    assert required_states == actual_values


def test_control_model_has_lifecycle_fields():
    """Control model exposes lifecycle management fields."""
    from controls.models import Control
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(Control)
    col_names = {col.key for col in mapper.columns}

    required_fields = {
        "lifecycle_status",
        "owner",
        "reviewer",
        "approved_at",
        "approved_by",
        "deprecated_at",
    }
    for field in required_fields:
        assert field in col_names, f"Missing lifecycle field: {field}"


def test_control_model_has_testability_fields():
    """Control model exposes testability metadata fields."""
    from controls.models import Control
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(Control)
    col_names = {col.key for col in mapper.columns}

    required_fields = {
        "test_what_en",
        "test_what_ar",
        "test_evidence_accepted",
        "test_frequency",
        "test_pass_criteria_en",
        "test_pass_criteria_ar",
    }
    for field in required_fields:
        assert field in col_names, f"Missing testability field: {field}"


def test_control_model_has_regulatory_source_fields():
    """Control model exposes regulatory source of truth fields."""
    from controls.models import Control
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(Control)
    col_names = {col.key for col in mapper.columns}

    required_fields = {
        "regulatory_source",
        "regulatory_version",
        "regulatory_article",
        "regulatory_page",
        "regulatory_effective_date",
    }
    for field in required_fields:
        assert field in col_names, f"Missing regulatory source field: {field}"


# ---------------------------------------------------------------------------
# Evidence tamper protection
# ---------------------------------------------------------------------------

def test_evidence_model_has_tamper_protection_fields():
    """Evidence model exposes SHA-256 tamper protection fields."""
    from evidence.models import Evidence
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(Evidence)
    col_names = {col.key for col in mapper.columns}

    required_fields = {
        "file_hash",
        "hash_algorithm",
        "hash_verified_at",
        "is_immutable",
    }
    for field in required_fields:
        assert field in col_names, f"Missing tamper protection field: {field}"


def test_evidence_model_has_workflow_fields():
    """Evidence model exposes Evidence Operating System workflow fields."""
    from evidence.models import Evidence
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(Evidence)
    col_names = {col.key for col in mapper.columns}

    required_fields = {
        "workflow_status",
        "submitted_at",
        "reviewed_at",
        "reviewed_by",
        "sla_due_date",
        "quality_score",
        "tenant_id",
    }
    for field in required_fields:
        assert field in col_names, f"Missing workflow field: {field}"


def test_evidence_workflow_status_enum():
    """EvidenceWorkflowStatus enum has all required states."""
    from evidence.models import EvidenceWorkflowStatus

    required_states = {
        "requested", "submitted", "under_review", "approved", "rejected", "expired",
    }
    actual_values = {s.value for s in EvidenceWorkflowStatus}
    assert required_states == actual_values


def test_compute_bytes_hash():
    """compute_bytes_hash returns correct SHA-256 digest."""
    from evidence.integrity import compute_bytes_hash
    import hashlib

    data = b"SICO GRC Platform - Saudi Regulatory Compliance"
    expected = hashlib.sha256(data).hexdigest()
    assert compute_bytes_hash(data) == expected
    assert len(compute_bytes_hash(data)) == 64


def test_compute_bytes_hash_deterministic():
    """Same input always produces the same hash."""
    from evidence.integrity import compute_bytes_hash

    data = b"test evidence content 12345"
    assert compute_bytes_hash(data) == compute_bytes_hash(data)


def test_compute_bytes_hash_different_inputs():
    """Different inputs produce different hashes."""
    from evidence.integrity import compute_bytes_hash

    assert compute_bytes_hash(b"content A") != compute_bytes_hash(b"content B")


def test_verify_file_hash_nonexistent_file():
    """verify_file_hash returns False for a missing file."""
    from evidence.integrity import verify_file_hash

    assert verify_file_hash("/tmp/nonexistent_sico_evidence_file.bin", "abc123") is False


def test_compute_file_hash(tmp_path):
    """compute_file_hash returns correct SHA-256 digest for a real file."""
    from evidence.integrity import compute_file_hash, verify_file_hash
    import hashlib

    content = b"This is a compliance document for NCA ECC-IS-3"
    file_path = tmp_path / "evidence.pdf"
    file_path.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest()
    computed = compute_file_hash(str(file_path))
    assert computed == expected_hash
    assert verify_file_hash(str(file_path), expected_hash) is True
    assert verify_file_hash(str(file_path), "wrong_hash") is False


# ---------------------------------------------------------------------------
# Regulatory module models
# ---------------------------------------------------------------------------

def test_regulatory_version_model_fields():
    """RegulatoryVersion model exposes required fields."""
    from regulatory.models import RegulatoryVersion
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(RegulatoryVersion)
    col_names = {col.key for col in mapper.columns}

    required_fields = {
        "framework", "version", "status", "release_date",
        "effective_date", "superseded_date", "official_url",
        "change_summary_en", "change_summary_ar",
    }
    for field in required_fields:
        assert field in col_names, f"Missing RegulatoryVersion field: {field}"


def test_tenant_config_model_fields():
    """TenantConfig model exposes required fields."""
    from regulatory.models import TenantConfig
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(TenantConfig)
    col_names = {col.key for col in mapper.columns}

    required_fields = {
        "tenant_id", "framework_scope", "language_preference",
        "evidence_policy_overrides", "client_dictionary",
        "ai_index_id", "ai_adapter_id", "sla_config",
    }
    for field in required_fields:
        assert field in col_names, f"Missing TenantConfig field: {field}"


# ---------------------------------------------------------------------------
# Pack definitions (commercial packs)
# ---------------------------------------------------------------------------

def test_pack_files_exist():
    """All three commercial pack JSON files are present and valid."""
    import json
    from pathlib import Path

    packs_dir = Path(__file__).resolve().parents[2] / "packs"
    expected_packs = [
        "ecc_baseline_pack.json",
        "ccc_cloud_pack.json",
        "pdpl_privacy_pack.json",
    ]
    for pack_file in expected_packs:
        path = packs_dir / pack_file
        assert path.exists(), f"Missing pack file: {pack_file}"
        with path.open() as fh:
            data = json.load(fh)
        assert "pack_id" in data
        assert "name_en" in data
        assert "name_ar" in data
        assert "deliverables" in data


def test_regulatory_version_register_exists():
    """Regulatory version register data file is present and valid."""
    import json
    from pathlib import Path

    reg_path = Path(__file__).resolve().parents[2] / "data" / "regulatory" / "version_register.json"
    assert reg_path.exists(), "version_register.json is missing"
    with reg_path.open() as fh:
        data = json.load(fh)
    assert "frameworks" in data
    for fw in ("ECC", "CCC", "PDPL"):
        assert fw in data["frameworks"], f"Framework {fw} missing from version register"
        assert "current_version" in data["frameworks"][fw]
        assert "versions" in data["frameworks"][fw]


def test_change_impact_workflow_exists():
    """Change impact workflow data file is present and valid."""
    import json
    from pathlib import Path

    workflow_path = (
        Path(__file__).resolve().parents[2] / "data" / "regulatory" / "change_impact_workflow.json"
    )
    assert workflow_path.exists(), "change_impact_workflow.json is missing"
    with workflow_path.open() as fh:
        data = json.load(fh)
    assert "workflow" in data
    assert "steps" in data["workflow"]
    assert len(data["workflow"]["steps"]) >= 5, "Workflow should have at least 5 steps"
