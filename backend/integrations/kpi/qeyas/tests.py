"""
Unit tests for the Qeyas KPI integration.

These tests mock all HTTP calls and database access so they run fast and
offline — no Qeyas server or database is required.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from integrations.models import IntegrationConfiguration
from integrations.kpi.qeyas.client import QeyasClient
from integrations.kpi.qeyas.mapper import QeyasFieldMapper
from integrations.kpi.qeyas.integration import QeyasOrchestrator


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_config():
    cfg = MagicMock(spec=IntegrationConfiguration)
    cfg.id = "00000000-0000-0000-0000-000000000001"
    cfg.credentials = {
        "api_url": "https://qeyas.example.com/api/v1",
        "api_key": "test-api-key",
    }
    cfg.settings = {
        "verify_ssl": False,
        "timeout": 5,
        "enable_outgoing_sync": True,
        "webhook_secret": "test-secret",
    }
    return cfg


@pytest.fixture
def client(mock_config):
    return QeyasClient(mock_config)


@pytest.fixture
def mapper(mock_config):
    return QeyasFieldMapper(mock_config)


@pytest.fixture
def orchestrator(mock_config):
    return QeyasOrchestrator(mock_config)


# ─────────────────────────────────────────────────────────────────────────────
# QeyasClient tests
# ─────────────────────────────────────────────────────────────────────────────


def test_client_raises_on_empty_base_url(mock_config):
    """Client must raise ValueError if neither credentials nor settings provide an API URL."""
    mock_config.credentials = {"api_url": "", "api_key": "key"}
    import django.conf as dc

    orig = dc.settings.QEYAS_API_URL
    try:
        dc.settings.QEYAS_API_URL = ""
        with pytest.raises(ValueError, match="Qeyas API URL is not configured"):
            QeyasClient(mock_config)
    finally:
        dc.settings.QEYAS_API_URL = orig
    mock_get.return_value.raise_for_status = MagicMock()
    mock_get.return_value.json.return_value = {"status": "ok"}
    assert client.test_connection() is True
    mock_get.assert_called_once()


@patch("integrations.kpi.qeyas.client.requests.get")
def test_test_connection_failure(mock_get, client):
    import requests as req

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"
    mock_get.side_effect = req.HTTPError(response=mock_resp)
    assert client.test_connection() is False


@patch("integrations.kpi.qeyas.client.requests.post")
def test_push_compliance_summary(mock_post, client):
    mock_post.return_value.raise_for_status = MagicMock()
    mock_post.return_value.json.return_value = {"id": "event-123"}
    result = client.push_compliance_summary({"event_type": "compliance.assessment.updated"})
    assert result["id"] == "event-123"
    mock_post.assert_called_once()
    call_url = mock_post.call_args[0][0]
    assert "/kpi/compliance-events" in call_url


@patch("integrations.kpi.qeyas.client.requests.get")
def test_get_kpi_summary(mock_get, client):
    mock_get.return_value.raise_for_status = MagicMock()
    mock_get.return_value.json.return_value = {"kpis": [], "total": 0}
    result = client.get_kpi_summary()
    assert "kpis" in result


# ─────────────────────────────────────────────────────────────────────────────
# QeyasFieldMapper tests
# ─────────────────────────────────────────────────────────────────────────────


def _make_compliance_assessment():
    """Build a minimal mock ComplianceAssessment."""
    framework = MagicMock()
    framework.ref_id = "sama-csf-1.0"
    framework.name = "SAMA Cyber Security Fundamentals"

    folder = MagicMock()
    folder.__str__ = lambda self: "Global / SICO"

    assessment = MagicMock()
    assessment.id = "aaaaaaaa-0000-0000-0000-000000000001"
    assessment.name = "SAMA CSF Assessment 2025"
    assessment.framework = framework
    assessment.status = "in_progress"
    assessment.progress = 65
    assessment.folder = folder
    assessment.updated_at = None
    assessment.get_global_score = MagicMock(return_value=3.2)
    return assessment


def _make_risk_assessment():
    """Build a minimal mock RiskAssessment."""
    folder = MagicMock()
    folder.__str__ = lambda self: "Global / SICO"

    assessment = MagicMock()
    assessment.id = "bbbbbbbb-0000-0000-0000-000000000002"
    assessment.name = "2025 Risk Assessment"
    assessment.status = "in_progress"
    assessment.folder = folder
    assessment.updated_at = None
    assessment.riskscenario_set.count = MagicMock(return_value=12)
    assessment.get_per_treatment = MagicMock(
        return_value={"reduce": 5, "accept": 3, "transfer": 2, "avoid": 2}
    )
    return assessment


def test_compliance_assessment_to_kpi_payload(mapper):
    assessment = _make_compliance_assessment()
    payload = QeyasFieldMapper.compliance_assessment_to_kpi_payload(assessment)

    assert payload["source"] == "sanadcom"
    assert payload["event_type"] == "compliance.assessment.updated"
    assert payload["assessment"]["id"] == str(assessment.id)
    assert payload["assessment"]["progress_pct"] == 65
    assert payload["assessment"]["framework"]["ref_id"] == "sama-csf-1.0"
    assert payload["assessment"]["global_score"] == 3.2


def test_risk_assessment_to_kpi_payload(mapper):
    assessment = _make_risk_assessment()
    payload = QeyasFieldMapper.risk_assessment_to_kpi_payload(assessment)

    assert payload["source"] == "sanadcom"
    assert payload["event_type"] == "risk.assessment.updated"
    assert payload["assessment"]["id"] == str(assessment.id)
    assert payload["assessment"]["scenarios"]["total"] == 12
    assert payload["assessment"]["scenarios"]["per_treatment"]["reduce"] == 5


# ─────────────────────────────────────────────────────────────────────────────
# QeyasOrchestrator tests
# ─────────────────────────────────────────────────────────────────────────────


@patch("integrations.kpi.qeyas.client.requests.post")
def test_push_compliance_assessment_success(mock_post, orchestrator):
    mock_post.return_value.raise_for_status = MagicMock()
    mock_post.return_value.json.return_value = {"id": "ev-001"}

    assessment = _make_compliance_assessment()
    result = orchestrator.push_compliance_assessment(assessment)
    assert result is True
    mock_post.assert_called_once()


@patch("integrations.kpi.qeyas.client.requests.post")
def test_push_compliance_assessment_disabled(mock_post, mock_config):
    mock_config.settings["enable_outgoing_sync"] = False
    orch = QeyasOrchestrator(mock_config)
    assessment = _make_compliance_assessment()
    result = orch.push_compliance_assessment(assessment)
    assert result is True
    mock_post.assert_not_called()


@patch("integrations.kpi.qeyas.client.requests.post")
def test_push_risk_assessment_success(mock_post, orchestrator):
    mock_post.return_value.raise_for_status = MagicMock()
    mock_post.return_value.json.return_value = {"id": "ev-002"}

    assessment = _make_risk_assessment()
    result = orchestrator.push_risk_assessment(assessment)
    assert result is True
    mock_post.assert_called_once()


def test_handle_webhook_kpi_threshold_breached(orchestrator):
    """Threshold-breached events should be logged and return True."""
    payload = {
        "event_type": "kpi.threshold.breached",
        "kpi_id": "kpi-123",
        "kpi_name": "Compliance Rate",
        "current_value": 45,
        "threshold": 80,
    }
    result = orchestrator.handle_webhook_event("kpi.threshold.breached", payload)
    assert result is True


def test_handle_webhook_unknown_event(orchestrator):
    """Unknown event types should be silently ignored (return True)."""
    result = orchestrator.handle_webhook_event("unknown.event", {})
    assert result is True


# ─────────────────────────────────────────────────────────────────────────────
# Integration registry tests
# ─────────────────────────────────────────────────────────────────────────────


def test_qeyas_provider_registered():
    """The Qeyas provider must be registered in the IntegrationRegistry."""
    from integrations.registry import IntegrationRegistry
    import integrations.kpi.qeyas.integration  # noqa: F401 — ensures registration

    provider = IntegrationRegistry.get_provider("qeyas")
    assert provider is not None
    assert provider.provider_type == "kpi"
    assert provider.client_class is QeyasClient
    assert provider.orchestrator_class is QeyasOrchestrator
