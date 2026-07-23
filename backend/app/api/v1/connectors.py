from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.connector import Connector
from app.schemas.connector import ConnectorCreate, ConnectorUpdate, ConnectorResponse
from app.services.connector_service import ConnectorService

router = APIRouter(prefix="/connectors", tags=["Connectors"])
connector_service = ConnectorService()

@router.post("", response_model=ConnectorResponse)
async def create_connector(
    data: ConnectorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    connector = Connector(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **data.model_dump()
    )
    db.add(connector)
    await db.commit()
    await db.refresh(connector)
    return connector

@router.get("", response_model=list[ConnectorResponse])
async def list_connectors(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Connector)
        .where(Connector.tenant_id == current_user.tenant_id, Connector.is_deleted == False)
        .order_by(desc(Connector.created_at))
    )
    return result.scalars().all()

@router.get("/{connector_id}", response_model=ConnectorResponse)
async def get_connector(
    connector_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Connector).where(
            Connector.id == connector_id,
            Connector.tenant_id == current_user.tenant_id
        )
    )
    connector = result.scalar_one_or_none()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector

@router.put("/{connector_id}", response_model=ConnectorResponse)
async def update_connector(
    connector_id: str,
    data: ConnectorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Connector).where(
            Connector.id == connector_id,
            Connector.tenant_id == current_user.tenant_id
        )
    )
    connector = result.scalar_one_or_none()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(connector, field, value)

    await db.commit()
    await db.refresh(connector)
    return connector

@router.delete("/{connector_id}")
async def delete_connector(
    connector_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Connector).where(
            Connector.id == connector_id,
            Connector.tenant_id == current_user.tenant_id
        )
    )
    connector = result.scalar_one_or_none()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    connector.is_deleted = True
    from datetime import datetime, timezone
    connector.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Connector deleted"}

@router.post("/{connector_id}/webhook")
async def receive_webhook(
    connector_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    payload = await request.json()
    result = await connector_service.process_incoming_webhook(db, connector_id, payload)
    return result
