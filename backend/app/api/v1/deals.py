from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.deal import Deal
from app.schemas.deal import DealCreate, DealUpdate, DealResponse

router = APIRouter(prefix="/deals", tags=["CRM - Deals"])

@router.get("", response_model=list[DealResponse])
async def list_deals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    result = await db.execute(
        select(Deal)
        .where(Deal.tenant_id == current_user.tenant_id, Deal.is_deleted == False)
        .order_by(desc(Deal.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("", response_model=DealResponse)
async def create_deal(
    data: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deal = Deal(
        tenant_id=current_user.tenant_id,
        **data.model_dump()
    )
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal

@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Deal).where(
            Deal.id == deal_id,
            Deal.tenant_id == current_user.tenant_id
        )
    )
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal

@router.put("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: str,
    data: DealUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Deal).where(
            Deal.id == deal_id,
            Deal.tenant_id == current_user.tenant_id
        )
    )
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(deal, field, value)

    await db.commit()
    await db.refresh(deal)
    return deal

@router.delete("/{deal_id}")
async def delete_deal(
    deal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Deal).where(
            Deal.id == deal_id,
            Deal.tenant_id == current_user.tenant_id
        )
    )
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    deal.is_deleted = True
    from datetime import datetime, timezone
    deal.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Deal deleted"}
