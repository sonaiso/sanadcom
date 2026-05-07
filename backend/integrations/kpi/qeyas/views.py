"""
Qeyas integration — Django views.

Provides:
  GET  /api/qeyas/executive-summary/   — unified GRC + KPI dashboard payload
  POST /api/qeyas/webhook/             — inbound events from Qeyas
"""

from __future__ import annotations

import json

import structlog
from django.conf import settings
from django.db.models import Avg, Count, Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = structlog.get_logger(__name__)


class QeyasExecutiveSummaryView(APIView):
    """
    Aggregated executive dashboard combining Sanadcom GRC data with the live
    KPI summary fetched from Qeyas.

    Returns HTTP 200 with the merged payload.  If Qeyas is unreachable the
    ``qeyas_summary`` key will contain ``{"error": "<reason>"}`` so the
    caller can still render the GRC section.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from core.models import (
            ComplianceAssessment,
            RiskAssessment,
            RiskScenario,
            AppliedControl,
        )

        # ── 1. GRC summary from Sanadcom ────────────────────────────────────
        # Compliance assessments
        ca_qs = ComplianceAssessment.objects.all()
        ca_total = ca_qs.count()
        ca_by_status = dict(
            ca_qs.values_list("status").annotate(cnt=Count("id")).values_list(
                "status", "cnt"
            )
        )
        # Average progress across in-progress assessments
        in_progress_cas = [
            ca
            for ca in ca_qs.filter(status="in_progress").select_related("framework")
        ]
        avg_progress = (
            round(
                sum(ca.progress for ca in in_progress_cas) / len(in_progress_cas),
                1,
            )
            if in_progress_cas
            else 0
        )

        # Risk assessments
        ra_qs = RiskAssessment.objects.all()
        ra_total = ra_qs.count()
        ra_by_status = dict(
            ra_qs.values_list("status").annotate(cnt=Count("id")).values_list(
                "status", "cnt"
            )
        )
        # Count open/critical risk scenarios
        critical_scenarios = RiskScenario.objects.filter(
            residual_level__gte=3  # adjust threshold per risk matrix
        ).count()
        open_scenarios = RiskScenario.objects.exclude(
            treatment="accepted"
        ).count()

        # Applied controls summary
        ac_qs = AppliedControl.objects.all()
        ac_by_status = dict(
            ac_qs.values_list("status").annotate(cnt=Count("id")).values_list(
                "status", "cnt"
            )
        )

        grc_summary = {
            "compliance_assessments": {
                "total": ca_total,
                "by_status": ca_by_status,
                "avg_progress_pct": avg_progress,
            },
            "risk_assessments": {
                "total": ra_total,
                "by_status": ra_by_status,
                "critical_scenarios": critical_scenarios,
                "open_scenarios": open_scenarios,
            },
            "applied_controls": {
                "by_status": ac_by_status,
            },
        }

        # ── 2. KPI summary from Qeyas ────────────────────────────────────────
        qeyas_summary = _fetch_qeyas_summary()

        return Response(
            {
                "grc_summary": grc_summary,
                "qeyas_summary": qeyas_summary,
            },
            status=status.HTTP_200_OK,
        )


class QeyasWebhookView(APIView):
    """
    Receives inbound webhook events from Qeyas (e.g. KPI threshold breached).

    Authentication is performed via HMAC-SHA256 signature validation using the
    ``webhook_secret`` stored in the matching IntegrationConfiguration.
    """

    authentication_classes = []  # Webhook auth is done via HMAC signature
    permission_classes = []

    def post(self, request):
        from integrations.models import IntegrationConfiguration
        from integrations.kpi.qeyas.integration import QeyasOrchestrator

        # Find the first active Qeyas configuration
        config = (
            IntegrationConfiguration.objects.filter(
                provider__name="qeyas", is_active=True
            )
            .select_related("provider")
            .first()
        )
        if config is None:
            return Response(
                {"detail": "No active Qeyas integration configured."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        orchestrator = QeyasOrchestrator(config)

        # Validate HMAC signature
        try:
            if not orchestrator.validate_webhook_request(request):
                return Response(
                    {"detail": "Invalid webhook signature."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse payload
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return Response(
                {"detail": "Invalid JSON payload."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event_type = orchestrator.extract_webhook_event_type(payload)
        orchestrator.handle_webhook_event(event_type, payload)

        return Response({"status": "received"}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _fetch_qeyas_summary() -> dict:
    """
    Attempt to fetch the KPI summary from the first active Qeyas configuration.
    Returns ``{"enabled": False}`` if Qeyas is not configured, or
    ``{"error": "<reason>"}`` if the API call fails.
    """
    if not settings.QEYAS_API_URL:
        return {"enabled": False}

    from integrations.models import IntegrationConfiguration

    config = (
        IntegrationConfiguration.objects.filter(
            provider__name="qeyas", is_active=True
        )
        .select_related("provider")
        .first()
    )
    if config is None:
        return {"enabled": False}

    from integrations.kpi.qeyas.client import QeyasClient

    client = QeyasClient(config)
    try:
        return client.get_kpi_summary()
    except Exception as exc:
        logger.warning("Failed to fetch Qeyas KPI summary", error=str(exc))
        return {"error": str(exc)}
