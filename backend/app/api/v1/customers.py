from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.models.contact import Contact
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, ContactCreate, ContactResponse

router = APIRouter(prefix="/customers", tags=["CRM - Customers"])

@router.post("", response_model=CustomerResponse)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = Customer(
        tenant_id=current_user.tenant_id,
        **data.model_dump()
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer

@router.get("", response_model=list[CustomerResponse])
async def list_customers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None
):
    query = select(Customer).where(
        Customer.tenant_id == current_user.tenant_id,
        Customer.is_deleted == False
    )

    if search:
        query = query.where(
            Customer.full_name.ilike(f"%{search}%") |
            Customer.email.ilike(f"%{search}%") |
            Customer.phone.ilike(f"%{search}%")
        )
    if status:
        query = query.where(Customer.status == status)
    if source:
        query = query.where(Customer.source == source)

    query = query.order_by(desc(Customer.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.tenant_id == current_user.tenant_id,
            Customer.is_deleted == False
        )
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.tenant_id == current_user.tenant_id
        )
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    await db.commit()
    await db.refresh(customer)
    return customer

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.tenant_id == current_user.tenant_id
        )
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.is_deleted = True
    from datetime import datetime, timezone
    customer.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Customer deleted"}

@router.post("/{customer_id}/contacts", response_model=ContactResponse)
async def add_contact(
    customer_id: str,
    data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = Contact(
        tenant_id=current_user.tenant_id,
        customer_id=customer_id,
        type=data.type,
        value=data.value,
        label=data.label,
        is_primary=data.is_primary
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

@router.get("/{customer_id}/contacts", response_model=list[ContactResponse])
async def list_contacts(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Contact).where(
            Contact.customer_id == customer_id,
            Contact.tenant_id == current_user.tenant_id
        )
    )
    return result.scalars().all()
