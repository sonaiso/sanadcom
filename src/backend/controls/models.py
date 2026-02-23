"""
Controls Module - ECC, CCC, PDPL Control Management
Handles bilingual control framework operations with full lifecycle management
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Date, Text, Enum, JSON, Boolean
import enum

from core.database import Base


class FrameworkType(str, enum.Enum):
    """Supported regulatory frameworks"""
    ECC = "ECC"
    CCC = "CCC"
    PDPL = "PDPL"


class ControlStatus(str, enum.Enum):
    """Control implementation status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"


class ControlLifecycleStatus(str, enum.Enum):
    """Control lifecycle status (content management, not compliance status)"""
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class Control(Base):
    """
    Bilingual Control Model
    Supports ECC, CCC, and PDPL frameworks with full lifecycle management.
    lifecycle_status tracks content state (Draft → Reviewed → Approved → Published → Deprecated).
    status tracks compliance state (not_started → in_progress → compliant / non_compliant).
    """
    __tablename__ = "controls"
    __table_args__ = {'extend_existing': True}  # Allow redefinition for compatibility

    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String(50), unique=True, index=True, nullable=False)
    framework = Column(String(10), nullable=False, index=True)
    domain = Column(String(100), nullable=False)

    # Bilingual content
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    description_en = Column(Text)
    description_ar = Column(Text)

    # Implementation guidance (bilingual)
    policy_guidance_en = Column(Text)
    policy_guidance_ar = Column(Text)
    procedure_guidance_en = Column(Text)
    procedure_guidance_ar = Column(Text)

    # Control metadata
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="not_started")
    maturity_level = Column(Integer, default=1)

    # JSON fields
    evidence_types = Column(JSON)
    related_controls = Column(JSON)

    # -----------------------------------------------------------------------
    # Lifecycle management (Phase 2.1 requirement)
    # -----------------------------------------------------------------------
    lifecycle_status = Column(String(20), default="published", index=True)
    owner = Column(String(200), nullable=True, index=True)
    reviewer = Column(String(200), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(200), nullable=True)
    deprecated_at = Column(DateTime, nullable=True)

    # -----------------------------------------------------------------------
    # Testability metadata (what to test, evidence accepted, pass/fail criteria)
    # -----------------------------------------------------------------------
    test_what_en = Column(Text, nullable=True)
    test_what_ar = Column(Text, nullable=True)
    test_evidence_accepted = Column(JSON, nullable=True)
    test_frequency = Column(String(50), nullable=True)     # e.g. "annual", "quarterly"
    test_pass_criteria_en = Column(Text, nullable=True)
    test_pass_criteria_ar = Column(Text, nullable=True)

    # -----------------------------------------------------------------------
    # Regulatory source of truth (traceability to official publications)
    # -----------------------------------------------------------------------
    regulatory_source = Column(String(100), nullable=True)   # e.g. "NCA ECC 1.0-2020"
    regulatory_version = Column(String(50), nullable=True)
    regulatory_article = Column(String(100), nullable=True)  # clause/section reference
    regulatory_page = Column(Integer, nullable=True)
    regulatory_effective_date = Column(Date, nullable=True)

    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Control {self.control_id} [{self.lifecycle_status}]: {self.title_en}>"

