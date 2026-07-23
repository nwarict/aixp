from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.automation import Automation

router = APIRouter(prefix="/automations", tags=["Automations"])

@router.get("")
async def list_automations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    result = await db.execute(
        select(Automation)
        .where(Automation.tenant_id == current_user.tenant_id, Automation.is_deleted == False)
        .order_by(desc(Automation.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("")
async def create_automation(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    automation = Automation(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        name=data.get("name"),
        description=data.get("description"),
        trigger_type=data.get("trigger_type"),
        trigger_config=data.get("trigger_config", {}),
        conditions=data.get("conditions", []),
        actions=data.get("actions", []),
        flow_data=data.get("flow_data", {}),
        status=data.get("status", "inactive")
    )
    db.add(automation)
    await db.commit()
    await db.refresh(automation)
    return automation

@router.get("/{automation_id}")
async def get_automation(
    automation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Automation).where(
            Automation.id == automation_id,
            Automation.tenant_id == current_user.tenant_id
        )
    )
    automation = result.scalar_one_or_none()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    return automation

@router.put("/{automation_id}")
async def update_automation(
    automation_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Automation).where(
            Automation.id == automation_id,
            Automation.tenant_id == current_user.tenant_id
        )
    )
    automation = result.scalar_one_or_none()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    for field, value in data.items():
        if hasattr(automation, field):
            setattr(automation, field, value)

    await db.commit()
    await db.refresh(automation)
    return automation

@router.delete("/{automation_id}")
async def delete_automation(
    automation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Automation).where(
            Automation.id == automation_id,
            Automation.tenant_id == current_user.tenant_id
        )
    )
    automation = result.scalar_one_or_none()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    automation.is_deleted = True
    from datetime import datetime, timezone
    automation.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Automation deleted"}
