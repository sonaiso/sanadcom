"""
Qeyas KPI Platform — orchestrator and integration registration.

This module registers the Qeyas integration provider with the
IntegrationRegistry so it is discovered automatically on Django startup.

The orchestrator is intentionally push-only: Sanadcom is the authoritative
source for GRC data and pushes compliance/risk summaries to Qeyas; it never
pulls KPI data back and modifies local GRC objects.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

import structlog
from django.conf import settings

from integrations.base import BaseSyncOrchestrator, BaseFieldMapper
from integrations.registry import IntegrationRegistry

from .client import QeyasClient
from .mapper import QeyasFieldMapper

logger = structlog.get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration schema (used for UI validation)
# ─────────────────────────────────────────────────────────────────────────────

QEYAS_CONFIG_SCHEMA: dict = {
    "required": ["credentials"],
    "credentials": {
        "required": ["api_url", "api_key"],
        "properties": {
            "api_url": {
                "type": "string",
                "description": "Base URL of the Qeyas REST API, e.g. https://qeyas.example.com/api/v1",
            },
            "api_key": {
                "type": "string",
                "description": "Bearer API key for M2M authentication with Qeyas",
            },
        },
    },
    "settings": {
        "properties": {
            "verify_ssl": {
                "type": "boolean",
                "default": True,
                "description": "Verify TLS certificates when calling Qeyas",
            },
            "timeout": {
                "type": "integer",
                "default": 30,
                "description": "HTTP timeout in seconds for Qeyas API calls",
            },
            "enable_outgoing_sync": {
                "type": "boolean",
                "default": True,
                "description": "Push GRC events to Qeyas when assessments change",
            },
            "webhook_secret": {
                "type": "string",
                "description": "HMAC secret used to validate inbound Qeyas webhooks",
            },
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────


class QeyasOrchestrator(BaseSyncOrchestrator):
    """
    Orchestrates the one-way push from Sanadcom GRC → Qeyas KPI.

    Supported operations
    ────────────────────
    * push_compliance_assessment(assessment)  — send a compliance summary
    * push_risk_assessment(assessment)        — send a risk summary
    * handle_webhook_event(event_type, payload) — receive KPI threshold alerts
    """

    client_class = QeyasClient
    mapper_class = QeyasFieldMapper

    def _get_client(self) -> QeyasClient:
        return QeyasClient(self.configuration)

    def _get_mapper(self) -> QeyasFieldMapper:
        return QeyasFieldMapper(self.configuration)

    # ── Push helpers ────────────────────────────────────────────────────────

    def push_compliance_assessment(self, assessment) -> bool:
        """Push a ComplianceAssessment summary to Qeyas."""
        if not self.configuration.settings.get("enable_outgoing_sync", True):
            logger.info(
                "Qeyas outgoing sync disabled for this configuration",
                config_id=str(self.configuration.id),
            )
            return True

        payload = QeyasFieldMapper.compliance_assessment_to_kpi_payload(assessment)
        try:
            self.client.push_compliance_summary(payload)
            logger.info(
                "Pushed compliance assessment to Qeyas",
                assessment_id=str(assessment.id),
                framework=payload["assessment"].get("framework", {}).get("ref_id"),
            )
            return True
        except Exception as exc:
            logger.error(
                "Failed to push compliance assessment to Qeyas",
                assessment_id=str(assessment.id),
                error=str(exc),
            )
            return False

    def push_risk_assessment(self, assessment) -> bool:
        """Push a RiskAssessment summary to Qeyas."""
        if not self.configuration.settings.get("enable_outgoing_sync", True):
            return True

        payload = QeyasFieldMapper.risk_assessment_to_kpi_payload(assessment)
        try:
            self.client.push_risk_summary(payload)
            logger.info(
                "Pushed risk assessment to Qeyas",
                assessment_id=str(assessment.id),
            )
            return True
        except Exception as exc:
            logger.error(
                "Failed to push risk assessment to Qeyas",
                assessment_id=str(assessment.id),
                error=str(exc),
            )
            return False

    # ── BaseSyncOrchestrator abstract methods ────────────────────────────────

    def _extract_remote_id(self, payload: dict[str, Any]) -> str:
        return str(payload.get("id", ""))

    def _extract_remote_data(self, payload: dict[str, Any]) -> dict[str, Any]:
        return payload

    # ── Inbound webhook from Qeyas ───────────────────────────────────────────

    def validate_webhook_request(self, request) -> bool:
        """Validate HMAC-SHA256 signature on inbound Qeyas webhook."""
        secret = self.configuration.settings.get("webhook_secret", "")
        if not secret:
            logger.warning(
                "Qeyas webhook secret not configured — accepting unsigned request",
                config_id=str(self.configuration.id),
            )
            return True

        signature_header = request.headers.get("X-Qeyas-Signature", "")
        if not signature_header:
            raise ValueError("Missing X-Qeyas-Signature header")

        expected = hmac.new(
            secret.encode(),
            request.body,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature_header, f"sha256={expected}")

    def extract_webhook_event_type(self, payload: dict) -> str:
        return payload.get("event_type", "")

    def handle_webhook_event(self, event_type: str, payload: dict[str, Any]) -> bool:
        """
        Handle inbound events from Qeyas (e.g. KPI threshold breached).

        Currently supported event types:
        * ``kpi.threshold.breached`` — log a warning; future work: create an
          Incident in Sanadcom automatically.
        * ``kpi.objective.updated``  — no-op; acknowledged but not acted on.
        """
        logger.info(
            "Received Qeyas webhook event",
            event_type=event_type,
            config_id=str(self.configuration.id),
        )

        if event_type == "kpi.threshold.breached":
            kpi_id = payload.get("kpi_id", "unknown")
            kpi_name = payload.get("kpi_name", "")
            current_value = payload.get("current_value")
            threshold = payload.get("threshold")
            logger.warning(
                "Qeyas KPI threshold breached",
                kpi_id=kpi_id,
                kpi_name=kpi_name,
                current_value=current_value,
                threshold=threshold,
            )
            return True

        if event_type == "kpi.objective.updated":
            logger.info(
                "Qeyas objective updated — no local action taken",
                objective_id=payload.get("objective_id"),
            )
            return True

        logger.info("Unhandled Qeyas webhook event type; ignoring", event_type=event_type)
        return True


# ─────────────────────────────────────────────────────────────────────────────
# Registration
# ─────────────────────────────────────────────────────────────────────────────

IntegrationRegistry.register(
    name="qeyas",
    provider_type="kpi",
    client_class=QeyasClient,
    mapper_class=QeyasFieldMapper,
    orchestrator_class=QeyasOrchestrator,
    display_name="Qeyas KPI Platform",
    description=(
        "Integration with the Qeyas KPI platform for the Saudi market. "
        "Pushes compliance and risk assessment summaries as KPI events."
    ),
    config_schema=QEYAS_CONFIG_SCHEMA,
)

logger.info("Qeyas KPI integration registered")
