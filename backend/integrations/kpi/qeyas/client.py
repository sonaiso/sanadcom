"""
Qeyas KPI Platform — REST API client.

Handles all HTTP communication with the Qeyas API.  Authentication is
performed via a Bearer API key stored in settings.QEYAS_API_KEY.

The client is deliberately stateless: each method creates its own request
so the same instance can safely be shared across threads / async contexts.
"""

from __future__ import annotations

from typing import Any

import requests
import structlog
from django.conf import settings

from integrations.base import BaseIntegrationClient

logger = structlog.get_logger(__name__)

_HEADERS_BASE = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


class QeyasClient(BaseIntegrationClient):
    """REST API client for the Qeyas KPI platform."""

    def __init__(self, configuration):
        super().__init__(configuration)
        self._base_url: str = (
            self.credentials.get("api_url") or settings.QEYAS_API_URL
        ).rstrip("/")
        self._api_key: str = (
            self.credentials.get("api_key") or settings.QEYAS_API_KEY
        )
        self._verify_ssl: bool = self.settings.get(
            "verify_ssl", settings.QEYAS_VERIFY_SSL
        )
        self._timeout: int = int(
            self.settings.get("timeout", settings.QEYAS_TIMEOUT)
        )

    # ──────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────

    def _headers(self) -> dict[str, str]:
        return {**_HEADERS_BASE, "Authorization": f"Bearer {self._api_key}"}

    def _url(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"

    def _get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        response = requests.get(
            self._url(path),
            headers=self._headers(),
            params=params,
            timeout=self._timeout,
            verify=self._verify_ssl,
        )
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, payload: dict) -> dict[str, Any]:
        response = requests.post(
            self._url(path),
            headers=self._headers(),
            json=payload,
            timeout=self._timeout,
            verify=self._verify_ssl,
        )
        response.raise_for_status()
        return response.json()

    def _put(self, path: str, payload: dict) -> dict[str, Any]:
        response = requests.put(
            self._url(path),
            headers=self._headers(),
            json=payload,
            timeout=self._timeout,
            verify=self._verify_ssl,
        )
        response.raise_for_status()
        return response.json()

    # ──────────────────────────────────────────────────────────────
    # BaseIntegrationClient interface
    # ──────────────────────────────────────────────────────────────

    def test_connection(self) -> bool:
        """Verify that the Qeyas API is reachable and the key is valid."""
        try:
            self._get("/health")
            return True
        except requests.HTTPError as exc:
            logger.warning(
                "Qeyas connection test failed",
                status=exc.response.status_code,
                detail=exc.response.text[:200],
            )
            return False
        except Exception as exc:
            logger.warning("Qeyas connection test failed", error=str(exc))
            return False

    def create_remote_object(self, local_object) -> str:
        """Push a new KPI sample to Qeyas and return the remote record ID."""
        from integrations.kpi.qeyas.mapper import QeyasFieldMapper

        mapper = QeyasFieldMapper(self.configuration)
        payload = mapper.to_remote(local_object)
        result = self._post("/kpi/samples", payload)
        return str(result.get("id", ""))

    def update_remote_object(self, remote_id: str, changes: dict[str, Any]) -> bool:
        """Update an existing KPI sample in Qeyas."""
        self._put(f"/kpi/samples/{remote_id}", changes)
        return True

    def get_remote_object(self, remote_id: str) -> dict[str, Any]:
        return self._get(f"/kpi/samples/{remote_id}")

    def list_remote_objects(
        self, query_params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        data = self._get("/kpi/samples", params=query_params)
        return data.get("results", data) if isinstance(data, dict) else data

    # ──────────────────────────────────────────────────────────────
    # Qeyas-specific helpers
    # ──────────────────────────────────────────────────────────────

    def push_compliance_summary(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Push a compliance summary event to Qeyas.

        The payload is expected to follow the shape produced by
        QeyasFieldMapper.compliance_assessment_to_kpi_payload().
        """
        return self._post("/kpi/compliance-events", payload)

    def push_risk_summary(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Push a risk assessment summary event to Qeyas.

        The payload is expected to follow the shape produced by
        QeyasFieldMapper.risk_assessment_to_kpi_payload().
        """
        return self._post("/kpi/risk-events", payload)

    def list_org_units(self) -> list[dict[str, Any]]:
        """Fetch the list of organisational units registered in Qeyas."""
        return self._get("/org-units")

    def get_kpi_summary(self) -> dict[str, Any]:
        """
        Fetch an aggregated KPI summary from Qeyas for use in the unified
        executive dashboard endpoint.
        """
        return self._get("/kpi/summary")
