from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageCreate, MessageResponse
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])
conversation_service = ConversationService()

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = await conversation_service.create_conversation(
        db=db,
        tenant_id=current_user.tenant_id,
        channel=data.channel,
        customer_id=data.customer_id,
        contact_id=data.contact_id,
        subject=data.subject,
        priority=data.priority,
        ai_enabled=data.ai_enabled
    )
    return conversation

@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    channel: Optional[str] = None,
    assigned_to: Optional[str] = None
):
    query = select(Conversation).where(
        Conversation.tenant_id == current_user.tenant_id,
        Conversation.is_deleted == False
    )

    if status:
        query = query.where(Conversation.status == status)
    if channel:
        query = query.where(Conversation.channel == channel)
    if assigned_to:
        query = query.where(Conversation.assigned_to == assigned_to)

    query = query.order_by(desc(Conversation.last_message_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == current_user.tenant_id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == current_user.tenant_id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(conversation, field, value)

    await db.commit()
    await db.refresh(conversation)
    return conversation

@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    result = await db.execute(
        select(Message).where(
            Message.conversation_id == conversation_id,
            Message.tenant_id == current_user.tenant_id
        )
        .order_by(desc(Message.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message = await conversation_service.add_message(
        db=db,
        conversation_id=conversation_id,
        tenant_id=current_user.tenant_id,
        sender_type="agent",
        sender_id=current_user.id,
        content=data.content,
        content_type=data.content_type
    )
    return message

@router.post("/{conversation_id}/ai-response")
async def trigger_ai_response(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == current_user.tenant_id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result_msg = await db.execute(
        select(Message).where(
            Message.conversation_id == conversation_id,
            Message.sender_type == "customer"
        )
        .order_by(desc(Message.created_at))
        .limit(1)
    )
    last_message = result_msg.scalar_one_or_none()

    if not last_message:
        raise HTTPException(status_code=400, detail="No customer message to respond to")

    ai_message = await conversation_service.process_ai_response(
        db=db,
        conversation_id=conversation_id,
        tenant_id=current_user.tenant_id,
        user_message=last_message.content
    )
    return {"status": "success", "message_id": ai_message.id}
