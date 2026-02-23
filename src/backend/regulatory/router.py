"""
Regulatory Module - API Router
Endpoints for regulatory version register and per-tenant configuration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime

from core.database import get_db
from regulatory.models import RegulatoryVersion, TenantConfig
from regulatory.schemas import (
    RegulatoryVersionCreate,
    RegulatoryVersionResponse,
    TenantConfigCreate,
    TenantConfigUpdate,
    TenantConfigResponse,
)

router = APIRouter(prefix="/regulatory", tags=["Regulatory"])


# ---------------------------------------------------------------------------
# Regulatory Version Register
# ---------------------------------------------------------------------------

@router.get("/versions", response_model=List[RegulatoryVersionResponse])
async def list_regulatory_versions(
    framework: Optional[str] = Query(None, description="Filter by framework (ECC, CCC, PDPL)"),
    status: Optional[str] = Query(None, description="Filter by status (active, superseded)"),
    db: AsyncSession = Depends(get_db),
):
    """
    List regulatory framework versions.
    Provides the authoritative Regulatory Source of Truth for all supported frameworks.
    """
    query = select(RegulatoryVersion)
    if framework:
        query = query.where(RegulatoryVersion.framework == framework.upper())
    if status:
        query = query.where(RegulatoryVersion.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/versions/{framework}/current", response_model=RegulatoryVersionResponse)
async def get_current_version(
    framework: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the currently active version for a framework."""
    result = await db.execute(
        select(RegulatoryVersion).where(
            RegulatoryVersion.framework == framework.upper(),
            RegulatoryVersion.status == "active",
        )
    )
    version = result.scalars().first()
    if not version:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"No active version found for framework {framework}",
                "message_ar": f"لا يوجد إصدار نشط للإطار {framework}",
            },
        )
    return version


@router.post("/versions", response_model=RegulatoryVersionResponse, status_code=201)
async def create_regulatory_version(
    payload: RegulatoryVersionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new regulatory framework version."""
    version = RegulatoryVersion(**payload.model_dump(), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return version


# ---------------------------------------------------------------------------
# Per-Tenant Configuration
# ---------------------------------------------------------------------------

@router.get("/tenants/{tenant_id}/config", response_model=TenantConfigResponse)
async def get_tenant_config(
    tenant_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve per-tenant configuration (framework scope, AI index, SLA, etc.)."""
    result = await db.execute(
        select(TenantConfig).where(TenantConfig.tenant_id == tenant_id)
    )
    config = result.scalars().first()
    if not config:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Configuration not found for tenant {tenant_id}",
                "message_ar": f"لم يُعثر على تهيئة للمستأجر {tenant_id}",
            },
        )
    return config


@router.post("/tenants/{tenant_id}/config", response_model=TenantConfigResponse, status_code=201)
async def create_tenant_config(
    tenant_id: int,
    payload: TenantConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create per-tenant configuration."""
    # Ensure tenant_id matches path
    payload_data = payload.model_dump()
    payload_data["tenant_id"] = tenant_id
    config = TenantConfig(**payload_data, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


@router.patch("/tenants/{tenant_id}/config", response_model=TenantConfigResponse)
async def update_tenant_config(
    tenant_id: int,
    payload: TenantConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update per-tenant configuration (partial update)."""
    result = await db.execute(
        select(TenantConfig).where(TenantConfig.tenant_id == tenant_id)
    )
    config = result.scalars().first()
    if not config:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Configuration not found for tenant {tenant_id}",
                "message_ar": f"لم يُعثر على تهيئة للمستأجر {tenant_id}",
            },
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    config.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(config)
    return config
