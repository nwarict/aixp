from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.connector import Connector
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.conversation_service import ConversationService

class ConnectorService:
    def __init__(self):
        self.conversation_service = ConversationService()

    async def process_incoming_webhook(
        self,
        db: AsyncSession,
        connector_id: str,
        payload: Dict[str, Any]
    ) -> Dict:
        """Process incoming webhook from any connector."""
        result = await db.execute(select(Connector).where(Connector.id == connector_id))
        connector = result.scalar_one_or_none()

        if not connector or connector.status != "active":
            return {"error": "Connector not found or inactive"}

        connector_type = connector.type

        if connector_type == "whatsapp":
            return await self._process_whatsapp(db, connector, payload)
        elif connector_type == "telegram":
            return await self._process_telegram(db, connector, payload)
        elif connector_type == "messenger":
            return await self._process_messenger(db, connector, payload)
        elif connector_type == "email":
            return await self._process_email(db, connector, payload)
        elif connector_type == "wordpress":
            return await self._process_wordpress(db, connector, payload)
        elif connector_type == "webhook":
            return await self._process_custom_webhook(db, connector, payload)
        else:
            return {"error": f"Unsupported connector type: {connector_type}"}

    async def _process_whatsapp(self, db, connector, payload):
        from_number = payload.get("from")
        message_body = payload.get("body")
        profile_name = payload.get("profile_name", "WhatsApp User")

        customer = await self.conversation_service.get_or_create_customer_from_message(
            db=db, tenant_id=connector.tenant_id, channel="whatsapp",
            sender_id=from_number, sender_name=profile_name
        )

        result = await db.execute(
            select(Conversation).where(
                Conversation.tenant_id == connector.tenant_id,
                Conversation.customer_id == customer.id,
                Conversation.channel == "whatsapp",
                Conversation.status.in_(["active", "waiting"])
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = await self.conversation_service.create_conversation(
                db=db, tenant_id=connector.tenant_id, channel="whatsapp",
                customer_id=customer.id, subject=f"WhatsApp: {message_body[:50]}"
            )

        message = await self.conversation_service.add_message(
            db=db, conversation_id=conversation.id, tenant_id=connector.tenant_id,
            sender_type="customer", sender_id=customer.id,
            content=message_body, external_id=payload.get("message_id")
        )

        if conversation.ai_enabled:
            ai_message = await self.conversation_service.process_ai_response(
                db=db, conversation_id=conversation.id,
                tenant_id=connector.tenant_id, user_message=message_body
            )
            return {"status": "success", "conversation_id": conversation.id, "message_id": message.id, "ai_response_id": ai_message.id}

        return {"status": "success", "conversation_id": conversation.id, "message_id": message.id}

    async def _process_telegram(self, db, connector, payload):
        chat_id = str(payload.get("message", {}).get("chat", {}).get("id"))
        text = payload.get("message", {}).get("text", "")
        from_user = payload.get("message", {}).get("from", {})
        username = from_user.get("first_name", "Telegram User")

        customer = await self.conversation_service.get_or_create_customer_from_message(
            db=db, tenant_id=connector.tenant_id, channel="telegram",
            sender_id=chat_id, sender_name=username
        )

        result = await db.execute(
            select(Conversation).where(
                Conversation.tenant_id == connector.tenant_id,
                Conversation.customer_id == customer.id,
                Conversation.channel == "telegram",
                Conversation.status.in_(["active", "waiting"])
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = await self.conversation_service.create_conversation(
                db=db, tenant_id=connector.tenant_id, channel="telegram",
                customer_id=customer.id, subject=f"Telegram: {text[:50]}"
            )

        message = await self.conversation_service.add_message(
            db=db, conversation_id=conversation.id, tenant_id=connector.tenant_id,
            sender_type="customer", sender_id=customer.id,
            content=text, external_id=str(payload.get("message", {}).get("message_id"))
        )

        if conversation.ai_enabled:
            ai_message = await self.conversation_service.process_ai_response(
                db=db, conversation_id=conversation.id,
                tenant_id=connector.tenant_id, user_message=text
            )
            return {"status": "success", "conversation_id": conversation.id, "message_id": message.id, "ai_response_id": ai_message.id}

        return {"status": "success", "conversation_id": conversation.id, "message_id": message.id}

    async def _process_messenger(self, db, connector, payload):
        """Process Facebook Messenger incoming message."""
        from app.connectors.messenger import MessengerConnector

        messenger = MessengerConnector(connector.config)
        msg_data = await messenger.receive_message(payload)

        sender_id = msg_data.get("sender_id")
        text = msg_data.get("text", "")

        if not sender_id or not text:
            return {"status": "ignored", "reason": "No message content"}

        customer = await self.conversation_service.get_or_create_customer_from_message(
            db=db, tenant_id=connector.tenant_id, channel="messenger",
            sender_id=sender_id, sender_name="Messenger User"
        )

        result = await db.execute(
            select(Conversation).where(
                Conversation.tenant_id == connector.tenant_id,
                Conversation.customer_id == customer.id,
                Conversation.channel == "messenger",
                Conversation.status.in_(["active", "waiting"])
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = await self.conversation_service.create_conversation(
                db=db, tenant_id=connector.tenant_id, channel="messenger",
                customer_id=customer.id, subject=f"Messenger: {text[:50]}"
            )

        message = await self.conversation_service.add_message(
            db=db, conversation_id=conversation.id, tenant_id=connector.tenant_id,
            sender_type="customer", sender_id=customer.id,
            content=text, external_id=msg_data.get("message_id")
        )

        if conversation.ai_enabled:
            ai_message = await self.conversation_service.process_ai_response(
                db=db, conversation_id=conversation.id,
                tenant_id=connector.tenant_id, user_message=text
            )
            return {"status": "success", "conversation_id": conversation.id, "message_id": message.id, "ai_response_id": ai_message.id}

        return {"status": "success", "conversation_id": conversation.id, "message_id": message.id}

    async def _process_email(self, db, connector, payload):
        from_email = payload.get("from")
        subject = payload.get("subject", "No Subject")
        body = payload.get("body", "")

        customer = await self.conversation_service.get_or_create_customer_from_message(
            db=db, tenant_id=connector.tenant_id, channel="email",
            sender_id=from_email, sender_name=from_email.split("@")[0]
        )

        result = await db.execute(
            select(Conversation).where(
                Conversation.tenant_id == connector.tenant_id,
                Conversation.customer_id == customer.id,
                Conversation.channel == "email",
                Conversation.status.in_(["active", "waiting"])
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = await self.conversation_service.create_conversation(
                db=db, tenant_id=connector.tenant_id, channel="email",
                customer_id=customer.id, subject=subject
            )

        message = await self.conversation_service.add_message(
            db=db, conversation_id=conversation.id, tenant_id=connector.tenant_id,
            sender_type="customer", sender_id=customer.id,
            content=body, content_type="html" if "<" in body else "text"
        )

        return {"status": "success", "conversation_id": conversation.id, "message_id": message.id}

    async def _process_wordpress(self, db, connector, payload):
        visitor_id = payload.get("visitor_id")
        message_text = payload.get("message")
        visitor_name = payload.get("name", "Website Visitor")
        page_url = payload.get("page_url", "")

        customer = await self.conversation_service.get_or_create_customer_from_message(
            db=db, tenant_id=connector.tenant_id, channel="website",
            sender_id=visitor_id, sender_name=visitor_name
        )

        result = await db.execute(
            select(Conversation).where(
                Conversation.tenant_id == connector.tenant_id,
                Conversation.customer_id == customer.id,
                Conversation.channel == "website",
                Conversation.status.in_(["active", "waiting"])
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = await self.conversation_service.create_conversation(
                db=db, tenant_id=connector.tenant_id, channel="website",
                customer_id=customer.id, subject=f"Website: {page_url}", ai_enabled=True
            )

        message = await self.conversation_service.add_message(
            db=db, conversation_id=conversation.id, tenant_id=connector.tenant_id,
            sender_type="customer", sender_id=customer.id, content=message_text
        )

        if conversation.ai_enabled:
            ai_message = await self.conversation_service.process_ai_response(
                db=db, conversation_id=conversation.id,
                tenant_id=connector.tenant_id, user_message=message_text
            )
            return {"status": "success", "conversation_id": conversation.id, "message_id": message.id, "ai_response_id": ai_message.id}

        return {"status": "success", "conversation_id": conversation.id, "message_id": message.id}

    async def _process_custom_webhook(self, db, connector, payload):
        return {"status": "received", "connector_id": connector.id, "payload_size": len(str(payload))}
