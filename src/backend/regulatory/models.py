"""
Regulatory Module - Models
Stores regulatory framework version register and per-tenant configuration.
"""

from datetime import datetime, date
from sqlalchemy import Column, String, Integer, DateTime, Date, Text, JSON, Boolean
import enum

from core.database import Base


class RegulatoryVersion(Base):
    """
    Regulatory Version Register - authoritative source of truth for each
    framework version.  Addresses requirement: Regulatory Source of Truth.
    """
    __tablename__ = "regulatory_versions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    framework = Column(String(20), nullable=False, index=True)      # ECC | CCC | PDPL
    version = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default='active')   # active | superseded
    release_date = Column(Date, nullable=True)
    effective_date = Column(Date, nullable=True)
    superseded_date = Column(Date, nullable=True)
    official_url = Column(String(500), nullable=True)
    source_document = Column(String(200), nullable=True)
    change_summary_en = Column(Text, nullable=True)
    change_summary_ar = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RegulatoryVersion {self.framework} {self.version} [{self.status}]>"


class TenantConfig(Base):
    """
    Per-tenant configuration for multi-tenant isolation.
    Stores framework scope, language preference, AI index IDs, SLA config,
    and client dictionary per tenant.
    """
    __tablename__ = "tenant_configs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, nullable=False, unique=True, index=True)
    framework_scope = Column(JSON, nullable=True)           # ["ECC", "CCC"]
    language_preference = Column(String(5), default='ar')  # "ar" | "en"
    evidence_policy_overrides = Column(JSON, nullable=True)
    report_template = Column(String(100), nullable=True)
    client_dictionary = Column(JSON, nullable=True)
    ai_index_id = Column(String(100), nullable=True)        # per-client Chroma index
    ai_adapter_id = Column(String(100), nullable=True)      # per-client LoRA adapter
    sla_config = Column(JSON, nullable=True)                # evidence SLA overrides
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TenantConfig tenant={self.tenant_id}>"
