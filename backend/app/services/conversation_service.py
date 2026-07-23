from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.customer import Customer
from app.models.contact import Contact
from app.services.ai_service import AIService

class ConversationService:
    def __init__(self):
        self.ai_service = AIService()

    async def create_conversation(
        self,
        db: AsyncSession,
        tenant_id: str,
        channel: str,
        customer_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        subject: Optional[str] = None,
        priority: str = "medium",
        ai_enabled: bool = True
    ) -> Conversation:
        conversation = Conversation(
            tenant_id=tenant_id,
            channel=channel,
            customer_id=customer_id,
            contact_id=contact_id,
            subject=subject,
            priority=priority,
            ai_enabled=ai_enabled
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        tenant_id: str,
        sender_type: str,
        sender_id: Optional[str],
        content: str,
        content_type: str = "text",
        is_ai_generated: bool = False,
        external_id: Optional[str] = None
    ) -> Message:
        message = Message(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_id=sender_id,
            content=content,
            content_type=content_type,
            is_ai_generated=is_ai_generated,
            external_id=external_id
        )
        db.add(message)

        # Update conversation last_message_at
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conversation = result.scalar_one_or_none()
        if conversation:
            from datetime import datetime, timezone
            conversation.last_message_at = datetime.now(timezone.utc).isoformat()

        await db.commit()
        await db.refresh(message)
        return message

    async def process_ai_response(
        self,
        db: AsyncSession,
        conversation_id: str,
        tenant_id: str,
        user_message: str
    ) -> Message:
        """Process AI response for a conversation."""
        # Get conversation context
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(5)
        )
        recent_messages = result.scalars().all()
        context = "\n".join([f"{'Customer' if m.sender_type == 'customer' else 'Agent'}: {m.content}" for m in reversed(recent_messages)])

        # Get AI response
        ai_result = await self.ai_service.chat(
            message=user_message,
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            context=context,
            use_knowledge=True,
            db=db
        )

        # Save AI message
        ai_message = await self.add_message(
            db=db,
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            sender_type="ai",
            sender_id=None,
            content=ai_result["response"],
            is_ai_generated=True
        )

        return ai_message

    async def get_or_create_customer_from_message(
        self,
        db: AsyncSession,
        tenant_id: str,
        channel: str,
        sender_id: str,
        sender_name: Optional[str] = None
    ) -> Customer:
        """Get or create customer from incoming message."""
        # Try to find existing contact
        result = await db.execute(
            select(Contact).where(
                Contact.tenant_id == tenant_id,
                Contact.type == channel,
                Contact.value == sender_id
            )
        )
        contact = result.scalar_one_or_none()

        if contact:
            result = await db.execute(select(Customer).where(Customer.id == contact.customer_id))
            return result.scalar_one()

        # Create new customer
        customer = Customer(
            tenant_id=tenant_id,
            full_name=sender_name or f"{channel.capitalize()} User",
            source=channel,
            status="active"
        )
        db.add(customer)
        await db.flush()

        # Create contact
        new_contact = Contact(
            tenant_id=tenant_id,
            customer_id=customer.id,
            type=channel,
            value=sender_id,
            is_primary=True
        )
        db.add(new_contact)
        await db.commit()
        await db.refresh(customer)

        return customer
