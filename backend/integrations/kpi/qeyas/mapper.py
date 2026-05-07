"""
Qeyas KPI Platform — field mapper.

Translates Sanadcom domain objects (ComplianceAssessment, RiskAssessment)
into the JSON payloads expected by the Qeyas REST API.
"""

from __future__ import annotations

from typing import Any

from django.utils import timezone

from integrations.base import BaseFieldMapper


class QeyasFieldMapper(BaseFieldMapper):
    """Maps Sanadcom GRC objects to Qeyas KPI payloads."""

    # Generic field mapping used by the BaseFieldMapper machinery.
    # The Qeyas-specific conversions are handled by the dedicated methods below.
    FIELD_MAPPINGS: dict[str, str] = {}

    # ──────────────────────────────────────────────────────────────
    # ComplianceAssessment → Qeyas KPI payload
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def compliance_assessment_to_kpi_payload(
        assessment,
    ) -> dict[str, Any]:
        """
        Build the Qeyas compliance-event payload for a ComplianceAssessment.

        The shape mirrors the anticipated Qeyas /kpi/compliance-events body:
        {
          "source": "sanadcom",
          "event_type": "compliance.assessment.updated",
          "timestamp": "<ISO-8601>",
          "assessment": {
            "id": "<uuid>",
            "name": "<str>",
            "framework": { "ref_id": "<str>", "name": "<str>" },
            "status": "<str>",
            "progress_pct": <int 0-100>,
            "global_score": <float|null>,
            "folder": "<str>",
            "last_updated": "<ISO-8601>"
          }
        }
        """
        framework = assessment.framework
        return {
            "source": "sanadcom",
            "event_type": "compliance.assessment.updated",
            "timestamp": timezone.now().isoformat(),
            "assessment": {
                "id": str(assessment.id),
                "name": assessment.name,
                "framework": {
                    "ref_id": framework.ref_id if framework else None,
                    "name": framework.name if framework else None,
                },
                "status": assessment.status,
                "progress_pct": assessment.progress,
                "global_score": _safe_score(assessment),
                "folder": str(assessment.folder) if assessment.folder else None,
                "last_updated": (
                    assessment.updated_at.isoformat()
                    if hasattr(assessment, "updated_at") and assessment.updated_at
                    else timezone.now().isoformat()
                ),
            },
        }

    # ──────────────────────────────────────────────────────────────
    # RiskAssessment → Qeyas KPI payload
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def risk_assessment_to_kpi_payload(assessment) -> dict[str, Any]:
        """
        Build the Qeyas risk-event payload for a RiskAssessment.

        Shape:
        {
          "source": "sanadcom",
          "event_type": "risk.assessment.updated",
          "timestamp": "<ISO-8601>",
          "assessment": {
            "id": "<uuid>",
            "name": "<str>",
            "status": "<str>",
            "scenarios": {
              "total": <int>,
              "per_treatment": { "<treatment>": <int>, ... }
            },
            "folder": "<str>",
            "last_updated": "<ISO-8601>"
          }
        }
        """
        return {
            "source": "sanadcom",
            "event_type": "risk.assessment.updated",
            "timestamp": timezone.now().isoformat(),
            "assessment": {
                "id": str(assessment.id),
                "name": assessment.name,
                "status": assessment.status,
                "scenarios": {
                    "total": assessment.riskscenario_set.count()
                    if hasattr(assessment, "riskscenario_set")
                    else 0,
                    "per_treatment": assessment.get_per_treatment()
                    if hasattr(assessment, "get_per_treatment")
                    else {},
                },
                "folder": str(assessment.folder) if assessment.folder else None,
                "last_updated": (
                    assessment.updated_at.isoformat()
                    if hasattr(assessment, "updated_at") and assessment.updated_at
                    else timezone.now().isoformat()
                ),
            },
        }


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _safe_score(assessment) -> float | None:
    """Return the global score for a ComplianceAssessment, or None if unavailable."""
    try:
        return assessment.get_global_score()
    except Exception:
        return None
