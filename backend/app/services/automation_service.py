from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.automation import Automation
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.lead import Lead
from app.services.ai_service import AIService

class AutomationService:
    def __init__(self):
        self.ai_service = AIService()

    async def evaluate_trigger(
        self,
        db: AsyncSession,
        trigger_type: str,
        trigger_data: Dict[str, Any]
    ) -> list:
        """Evaluate all automations for a given trigger."""
        tenant_id = trigger_data.get("tenant_id")

        result = await db.execute(
            select(Automation).where(
                Automation.tenant_id == tenant_id,
                Automation.status == "active",
                Automation.trigger_type == trigger_type
            )
        )
        automations = result.scalars().all()

        triggered = []
        for automation in automations:
            if await self._check_conditions(automation, trigger_data):
                triggered.append(automation)

        return triggered

    async def _check_conditions(self, automation: Automation, trigger_data: Dict) -> bool:
        """Check if automation conditions are met."""
        conditions = automation.conditions
        if not conditions:
            return True

        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")

            actual_value = trigger_data.get(field)

            if operator == "equals" and actual_value != value:
                return False
            elif operator == "contains" and value not in str(actual_value):
                return False
            elif operator == "greater_than" and (actual_value is None or float(actual_value) <= float(value)):
                return False
            elif operator == "less_than" and (actual_value is None or float(actual_value) >= float(value)):
                return False

        return True

    async def execute_actions(
        self,
        db: AsyncSession,
        automation: Automation,
        trigger_data: Dict
    ) -> Dict:
        """Execute automation actions."""
        results = []

        for action in automation.actions:
            action_type = action.get("type")

            try:
                if action_type == "send_message":
                    result = await self._action_send_message(db, action, trigger_data)
                elif action_type == "create_task":
                    result = await self._action_create_task(db, action, trigger_data)
                elif action_type == "create_lead":
                    result = await self._action_create_lead(db, action, trigger_data)
                elif action_type == "assign_conversation":
                    result = await self._action_assign_conversation(db, action, trigger_data)
                elif action_type == "send_webhook":
                    result = await self._action_send_webhook(action, trigger_data)
                elif action_type == "ai_response":
                    result = await self._action_ai_response(db, action, trigger_data)
                else:
                    result = {"status": "error", "message": f"Unknown action type: {action_type}"}

                results.append(result)
            except Exception as e:
                results.append({"status": "error", "message": str(e)})

        # Update automation stats
        automation.execution_count += 1
        from datetime import datetime, timezone
        automation.last_executed_at = datetime.now(timezone.utc).isoformat()
        await db.commit()

        return {"automation_id": automation.id, "results": results}

    async def _action_send_message(self, db, action, trigger_data):
        from app.services.conversation_service import ConversationService
        service = ConversationService()

        conversation_id = trigger_data.get("conversation_id")
        content = action.get("content", "")

        # Replace variables
        for key, value in trigger_data.items():
            content = content.replace(f"{{{key}}}", str(value))

        message = await service.add_message(
            db=db,
            conversation_id=conversation_id,
            tenant_id=trigger_data["tenant_id"],
            sender_type="system",
            sender_id=None,
            content=content
        )
        return {"status": "success", "message_id": message.id}

    async def _action_create_task(self, db, action, trigger_data):
        from app.models.task import Task
        task = Task(
            tenant_id=trigger_data["tenant_id"],
            title=action.get("title", "Automated Task"),
            description=action.get("description", ""),
            assigned_to=action.get("assigned_to"),
            related_type=trigger_data.get("entity_type"),
            related_id=trigger_data.get("entity_id"),
            priority=action.get("priority", "medium")
        )
        db.add(task)
        await db.commit()
        return {"status": "success", "task_id": task.id}

    async def _action_create_lead(self, db, action, trigger_data):
        from app.models.lead import Lead
        lead = Lead(
            tenant_id=trigger_data["tenant_id"],
            title=action.get("title", "New Lead"),
            description=action.get("description", ""),
            source="automation",
            assigned_to=action.get("assigned_to"),
            status="new"
        )
        db.add(lead)
        await db.commit()
        return {"status": "success", "lead_id": lead.id}

    async def _action_assign_conversation(self, db, action, trigger_data):
        conversation_id = trigger_data.get("conversation_id")
        user_id = action.get("user_id")

        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.assigned_to = user_id
            await db.commit()
            return {"status": "success", "assigned_to": user_id}
        return {"status": "error", "message": "Conversation not found"}

    async def _action_send_webhook(self, action, trigger_data):
        import httpx
        url = action.get("url")
        headers = action.get("headers", {})

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=trigger_data, headers=headers, timeout=10.0)
            return {"status": "success", "status_code": response.status_code}

    async def _action_ai_response(self, db, action, trigger_data):
        from app.services.conversation_service import ConversationService
        service = ConversationService()

        conversation_id = trigger_data.get("conversation_id")
        tenant_id = trigger_data["tenant_id"]

        ai_message = await service.process_ai_response(
            db=db,
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            user_message=trigger_data.get("message_content", "")
        )
        return {"status": "success", "message_id": ai_message.id}
