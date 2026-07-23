from app.connectors.base import BaseConnector

class MessengerConnector(BaseConnector):
    async def send_message(self, recipient: str, content: str, **kwargs):
        """Send message via Facebook Messenger Graph API."""
        import httpx
        from app.core.config import get_settings
        settings = get_settings()

        page_access_token = self.config.get("page_access_token") or settings.meta_page_access_token
        if not page_access_token:
            return {"status": "error", "message": "Page access token not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://graph.facebook.com/v18.0/me/messages",
                    params={"access_token": page_access_token},
                    json={
                        "recipient": {"id": recipient},
                        "message": {"text": content}
                    },
                    timeout=30.0
                )
                data = response.json()
                if "error" in data:
                    return {"status": "error", "message": data["error"].get("message", "Unknown error")}
                return {"status": "success", "message_id": data.get("message_id")}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def receive_message(self, payload: dict):
        """Parse Facebook Messenger webhook payload."""
        entry = payload.get("entry", [{}])[0]
        messaging = entry.get("messaging", [{}])[0]

        sender = messaging.get("sender", {})
        message = messaging.get("message", {})

        return {
            "sender_id": sender.get("id"),
            "page_id": entry.get("id"),
            "message_id": message.get("mid"),
            "text": message.get("text", ""),
            "attachments": message.get("attachments", []),
            "timestamp": messaging.get("timestamp")
        }

    async def verify_webhook(self, request_data: dict):
        """Verify Facebook webhook challenge."""
        from app.core.config import get_settings
        settings = get_settings()

        mode = request_data.get("hub.mode")
        token = request_data.get("hub.verify_token")
        verify_token = self.config.get("verify_token") or settings.meta_verify_token

        return mode == "subscribe" and token == verify_token

    def get_webhook_response(self, request_data: dict):
        """Return challenge response for webhook verification."""
        return request_data.get("hub.challenge", "")
