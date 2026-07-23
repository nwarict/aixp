from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.contact import Contact

router = APIRouter(prefix="/contacts", tags=["CRM - Contacts"])

@router.get("")
async def list_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    customer_id: str = None,
    skip: int = 0,
    limit: int = 100
):
    query = select(Contact).where(
        Contact.tenant_id == current_user.tenant_id,
        Contact.is_deleted == False
    )
    if customer_id:
        query = query.where(Contact.customer_id == customer_id)

    query = query.order_by(desc(Contact.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{contact_id}")
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Contact).where(
            Contact.id == contact_id,
            Contact.tenant_id == current_user.tenant_id
        )
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}")
async def update_contact(
    contact_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Contact).where(
            Contact.id == contact_id,
            Contact.tenant_id == current_user.tenant_id
        )
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for field, value in data.items():
        if hasattr(contact, field):
            setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)
    return contact

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Contact).where(
            Contact.id == contact_id,
            Contact.tenant_id == current_user.tenant_id
        )
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.is_deleted = True
    from datetime import datetime, timezone
    contact.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Contact deleted"}
