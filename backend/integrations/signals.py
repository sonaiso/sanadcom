"""
integrations/signals.py

Django signal handlers that automatically trigger background pushes to all
active Qeyas KPI configurations whenever a ComplianceAssessment or
RiskAssessment is saved.

Design notes
────────────
* Handlers are registered via ``IntegrationsConfig.ready()`` (see apps.py).
* All model imports live inside the handlers to avoid circular imports.
* Tasks are enqueued via ``transaction.on_commit`` so the DB row is fully
  committed before the Huey worker tries to read it.
* ``dispatch_uid`` strings make the registrations idempotent even if this
  module is accidentally imported multiple times.
* Both handlers silently bail out when no active Qeyas configuration exists,
  so adding the integration has zero runtime cost on installations that have
  not configured it.
"""

from __future__ import annotations

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

import structlog

logger = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _qeyas_enabled() -> bool:
    """Return True if at least one active Qeyas configuration exists."""
    from integrations.models import IntegrationConfiguration

    return IntegrationConfiguration.objects.filter(
        provider__name="qeyas",
        is_active=True,
    ).exists()


# ─────────────────────────────────────────────────────────────────────────────
# ComplianceAssessment → Qeyas push
# ─────────────────────────────────────────────────────────────────────────────


@receiver(
    post_save,
    sender="core.ComplianceAssessment",
    dispatch_uid="integrations.compliance_assessment_post_save_qeyas",
)
def on_compliance_assessment_saved(
    sender, instance, created: bool, **kwargs
) -> None:
    """
    Enqueue a Qeyas push whenever a ComplianceAssessment is created or updated.

    The task is scheduled *after* the current DB transaction commits so the
    Huey worker always reads a fully persisted row.  The Qeyas-enabled check
    also runs post-commit to avoid a wasted DB round-trip on rolled-back saves.
    """
    assessment_id = str(instance.pk)

    def _enqueue():
        try:
            if not _qeyas_enabled():
                return
            from core.tasks import push_compliance_assessment_to_qeyas

            push_compliance_assessment_to_qeyas.schedule(args=(assessment_id,), delay=1)
            logger.debug(
                "Enqueued push_compliance_assessment_to_qeyas",
                assessment_id=assessment_id,
                created=created,
            )
        except Exception:
            logger.exception(
                "on_compliance_assessment_saved: failed to enqueue Qeyas push",
                assessment_id=assessment_id,
            )

    transaction.on_commit(_enqueue)


# ─────────────────────────────────────────────────────────────────────────────
# RiskAssessment → Qeyas push
# ─────────────────────────────────────────────────────────────────────────────


@receiver(
    post_save,
    sender="core.RiskAssessment",
    dispatch_uid="integrations.risk_assessment_post_save_qeyas",
)
def on_risk_assessment_saved(
    sender, instance, created: bool, **kwargs
) -> None:
    """
    Enqueue a Qeyas push whenever a RiskAssessment is created or updated.
    """
    assessment_id = str(instance.pk)

    def _enqueue():
        try:
            if not _qeyas_enabled():
                return
            from core.tasks import push_risk_assessment_to_qeyas

            push_risk_assessment_to_qeyas.schedule(args=(assessment_id,), delay=1)
            logger.debug(
                "Enqueued push_risk_assessment_to_qeyas",
                assessment_id=assessment_id,
                created=created,
            )
        except Exception:
            logger.exception(
                "on_risk_assessment_saved: failed to enqueue Qeyas push",
                assessment_id=assessment_id,
            )

    transaction.on_commit(_enqueue)
