"""
Regulatory Module - Pydantic Schemas
"""

from datetime import datetime, date
from typing import Optional, List, Any, Dict
from pydantic import BaseModel


class RegulatoryVersionBase(BaseModel):
    framework: str
    version: str
    status: str = "active"
    release_date: Optional[date] = None
    effective_date: Optional[date] = None
    superseded_date: Optional[date] = None
    official_url: Optional[str] = None
    source_document: Optional[str] = None
    change_summary_en: Optional[str] = None
    change_summary_ar: Optional[str] = None


class RegulatoryVersionCreate(RegulatoryVersionBase):
    pass


class RegulatoryVersionResponse(RegulatoryVersionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TenantConfigBase(BaseModel):
    tenant_id: int
    framework_scope: Optional[List[str]] = None
    language_preference: str = "ar"
    evidence_policy_overrides: Optional[Dict[str, Any]] = None
    report_template: Optional[str] = None
    client_dictionary: Optional[Dict[str, Any]] = None
    ai_index_id: Optional[str] = None
    ai_adapter_id: Optional[str] = None
    sla_config: Optional[Dict[str, Any]] = None


class TenantConfigCreate(TenantConfigBase):
    pass


class TenantConfigUpdate(BaseModel):
    framework_scope: Optional[List[str]] = None
    language_preference: Optional[str] = None
    evidence_policy_overrides: Optional[Dict[str, Any]] = None
    report_template: Optional[str] = None
    client_dictionary: Optional[Dict[str, Any]] = None
    ai_index_id: Optional[str] = None
    ai_adapter_id: Optional[str] = None
    sla_config: Optional[Dict[str, Any]] = None


class TenantConfigResponse(TenantConfigBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
