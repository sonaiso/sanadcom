"""
Evidence Module - Models
Manages audit evidence collection and validation with tamper protection
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
import enum

from core.database import Base


class EvidenceStatus(str, enum.Enum):
    """Evidence collection status"""
    PENDING = "pending"
    COLLECTED = "collected"
    VALIDATED = "validated"
    REJECTED = "rejected"
    EXPIRED = "expired"


class EvidenceWorkflowStatus(str, enum.Enum):
    """Evidence operational workflow state"""
    REQUESTED = "requested"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class EvidenceType(str, enum.Enum):
    """Types of evidence"""
    POLICY = "policy"
    PROCEDURE = "procedure"
    LOG = "log"
    SCREENSHOT = "screenshot"
    REPORT = "report"
    CERTIFICATE = "certificate"
    OTHER = "other"


class Evidence(Base):
    """
    Evidence Model - Tracks compliance evidence with tamper protection.
    file_hash (SHA-256) and workflow_status fields implement the Evidence
    Operating System requirements (collection workflow, SLA, tamper protection).
    """
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(String(100), unique=True, index=True, nullable=False)

    # Link to control
    control_id = Column(String(50), ForeignKey("controls.control_id"), nullable=False)

    # Evidence metadata
    evidence_type = Column(Enum(EvidenceType), nullable=False)
    status = Column(Enum(EvidenceStatus), default=EvidenceStatus.PENDING)

    # Bilingual fields
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    description_en = Column(Text)
    description_ar = Column(Text)

    # File information
    file_path = Column(String(1000))
    file_name = Column(String(500))
    file_size = Column(Integer)   # in bytes
    file_format = Column(String(50))   # PDF, DOCX, etc.

    # -----------------------------------------------------------------------
    # Tamper protection (SHA-256 hash + integrity verification)
    # -----------------------------------------------------------------------
    file_hash = Column(String(64), nullable=True)       # SHA-256 hex digest of file content
    hash_algorithm = Column(String(20), nullable=True)  # "SHA-256"
    hash_verified_at = Column(DateTime, nullable=True)  # last integrity check timestamp
    is_immutable = Column(Boolean, default=False)       # True once approved; prevents modification

    # -----------------------------------------------------------------------
    # Evidence Operating System - workflow states and SLA tracking
    # -----------------------------------------------------------------------
    workflow_status = Column(String(30), default="requested", index=True)
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(200), nullable=True)
    sla_due_date = Column(DateTime, nullable=True)      # deadline per evidence SLA policy
    quality_score = Column(Integer, nullable=True)      # 0–100 completeness/quality score

    # Multi-tenant isolation
    tenant_id = Column(Integer, nullable=True, index=True)

    # Validation
    validated_by = Column(String(200))
    validated_at = Column(DateTime)
    validation_notes = Column(Text)

    # Retention
    collection_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    retention_period_days = Column(Integer, default=2555)  # 7 years default

    # Additional metadata
    additional_metadata = Column(JSON)   # flexible data (renamed from 'metadata' to avoid SQLAlchemy conflict)

    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(200))

    def __repr__(self):
        return f"<Evidence {self.evidence_id} [{self.workflow_status}]: {self.title_en}>"

