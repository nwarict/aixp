from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy import text as sql_text

from app.core.db import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.models.tenant import Tenant
from app.models.customer import Customer
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.lead import Lead
from app.models.campaign import Campaign

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
async def admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    tenant_id = current_user.tenant_id

    customer_count = await db.execute(
        select(func.count(Customer.id)).where(
            Customer.tenant_id == tenant_id,
            Customer.is_deleted == False
        )
    )
    conversation_count = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.tenant_id == tenant_id,
            Conversation.is_deleted == False
        )
    )
    active_conversations = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.tenant_id == tenant_id,
            Conversation.status.in_(["active", "waiting"])
        )
    )
    lead_count = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id,
            Lead.is_deleted == False
        )
    )
    message_count = await db.execute(
        select(func.count(Message.id)).where(
            Message.tenant_id == tenant_id
        )
    )
    campaign_count = await db.execute(
        select(func.count(Campaign.id)).where(
            Campaign.tenant_id == tenant_id,
            Campaign.is_deleted == False
        )
    )

    recent_conversations = await db.execute(
        select(Conversation).where(
            Conversation.tenant_id == tenant_id
        )
        .order_by(desc(Conversation.last_message_at))
        .limit(10)
    )

    channel_stats = await db.execute(
        sql_text("""
            SELECT channel, COUNT(*) as count 
            FROM conversations 
            WHERE tenant_id = :tenant_id AND is_deleted = false
            GROUP BY channel
        """),
        {"tenant_id": tenant_id}
    )

    return {
        "stats": {
            "customers": customer_count.scalar(),
            "conversations": conversation_count.scalar(),
            "active_conversations": active_conversations.scalar(),
            "leads": lead_count.scalar(),
            "messages": message_count.scalar(),
            "campaigns": campaign_count.scalar()
        },
        "recent_conversations": [
            {"id": c.id, "channel": c.channel, "status": c.status, "subject": c.subject}
            for c in recent_conversations.scalars().all()
        ],
        "channel_stats": [dict(r._mapping) for r in channel_stats.fetchall()]
    }

@router.get("/tenants")
async def list_tenants(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin only")

    result = await db.execute(select(Tenant).order_by(desc(Tenant.created_at)))
    tenants = result.scalars().all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "slug": t.slug,
            "plan": t.plan,
            "is_active": t.is_active,
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        for t in tenants
    ]
