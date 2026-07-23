import httpx
from typing import Optional
from app.core.config import get_settings
from app.connectors.base import BaseConnector

settings = get_settings()

class WhatsAppConnector(BaseConnector):
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.api_key = config.get("api_key") or settings.whatsapp_api_key
        self.api_url = config.get("api_url", "https://graph.facebook.com/v18.0")
        self.phone_number_id = config.get("phone_number_id", "")

    async def send_message(self, to: str, text: str) -> dict:
        """Send WhatsApp message via Business API."""
        if not self.api_key:
            return {"success": False, "error": "WhatsApp API key not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": to,
                        "type": "text",
                        "text": {"body": text}
                    }
                )
                data = response.json()
                if "messages" in data:
                    return {"success": True, "message_id": data["messages"][0]["id"]}
                return {"success": False, "error": data.get("error", {}).get("message", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def send_template(self, to: str, template_name: str, language_code: str = "ar") -> dict:
        """Send a template message."""
        if not self.api_key:
            return {"success": False, "error": "WhatsApp API key not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/{self.phone_number_id}/messages",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "messaging_product": "whatsapp",
                        "to": to,
                        "type": "template",
                        "template": {
                            "name": template_name,
                            "language": {"code": language_code}
                        }
                    }
                )
                data = response.json()
                if "messages" in data:
                    return {"success": True, "message_id": data["messages"][0]["id"]}
                return {"success": False, "error": data.get("error", {}).get("message")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def verify_connection(self) -> bool:
        """Verify WhatsApp API connection."""
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/me",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.status_code == 200
        except Exception:
            return False
