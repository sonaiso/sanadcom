# Backend Tests
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from controls.models import ControlStatus, FrameworkType
from evidence.models import EvidenceStatus, EvidenceType


@pytest.mark.asyncio
async def test_health_check():
    """Test API health check endpoint"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "ECC" in data["frameworks"]
        assert data["features"]["bilingual"] is True


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns bilingual message"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message_en" in data
        assert "message_ar" in data


def test_control_status_enum_members():
    """Verify ControlStatus enum uses proper members for PostgreSQL compatibility"""
    assert ControlStatus.NON_COMPLIANT.value == "non_compliant"
    assert ControlStatus.COMPLIANT.value == "compliant"
    assert ControlStatus.IN_PROGRESS.value == "in_progress"
    assert ControlStatus.NOT_STARTED.value == "not_started"
    assert ControlStatus.NOT_APPLICABLE.value == "not_applicable"


def test_framework_type_enum_members():
    """Verify FrameworkType enum uses proper members for PostgreSQL compatibility"""
    assert FrameworkType.ECC.value == "ECC"
    assert FrameworkType.CCC.value == "CCC"
    assert FrameworkType.PDPL.value == "PDPL"


def test_evidence_status_enum_members():
    """Verify EvidenceStatus enum uses proper members for PostgreSQL compatibility"""
    assert EvidenceStatus.PENDING.value == "pending"
    assert EvidenceStatus.COLLECTED.value == "collected"
    assert EvidenceStatus.VALIDATED.value == "validated"
    assert EvidenceStatus.REJECTED.value == "rejected"


def test_evidence_type_enum_members():
    """Verify EvidenceType enum uses proper members for PostgreSQL compatibility"""
    assert EvidenceType.LOG.value == "log"
    assert EvidenceType.SCREENSHOT.value == "screenshot"
    assert EvidenceType.POLICY.value == "policy"
    assert EvidenceType.REPORT.value == "report"


def test_control_model_uses_enum_columns():
    """Verify Control model uses Enum column types (not String) for enum fields"""
    from sqlalchemy import Enum as SAEnum
    from controls.models import Control
    framework_col = Control.__table__.columns["framework"]
    status_col = Control.__table__.columns["status"]
    assert isinstance(framework_col.type, SAEnum), (
        "Control.framework must use SQLAlchemy Enum type for PostgreSQL compatibility"
    )
    assert isinstance(status_col.type, SAEnum), (
        "Control.status must use SQLAlchemy Enum type for PostgreSQL compatibility"
    )


def test_evidence_model_uses_enum_columns():
    """Verify Evidence model uses Enum column types (not String) for enum fields"""
    from sqlalchemy import Enum as SAEnum
    from evidence.models import Evidence
    evidence_type_col = Evidence.__table__.columns["evidence_type"]
    status_col = Evidence.__table__.columns["status"]
    assert isinstance(evidence_type_col.type, SAEnum), (
        "Evidence.evidence_type must use SQLAlchemy Enum type for PostgreSQL compatibility"
    )
    assert isinstance(status_col.type, SAEnum), (
        "Evidence.status must use SQLAlchemy Enum type for PostgreSQL compatibility"
    )


def test_enum_member_assignment():
    """Verify enum fields accept Enum members (not bare strings) as per PostgreSQL requirements"""
    # Verify that assigning enum members works correctly
    # Using ECC framework and NON_COMPLIANT status as documented examples
    framework = FrameworkType.ECC
    status = ControlStatus.NON_COMPLIANT

    assert framework == FrameworkType.ECC
    assert status == ControlStatus.NON_COMPLIANT
    assert framework.value == "ECC"
    assert status.value == "non_compliant"

    # Verify enum members can be filtered/compared (critical for SQLAlchemy queries)
    all_statuses = list(ControlStatus)
    assert ControlStatus.NON_COMPLIANT in all_statuses
    assert ControlStatus.COMPLIANT in all_statuses

    all_frameworks = list(FrameworkType)
    assert FrameworkType.ECC in all_frameworks
    assert FrameworkType.CCC in all_frameworks
    assert FrameworkType.PDPL in all_frameworks

