import httpx
from typing import Optional
from app.core.config import get_settings
from app.connectors.base import BaseConnector

settings = get_settings()

class TelegramConnector(BaseConnector):
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.bot_token = config.get("bot_token") or settings.telegram_bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> dict:
        """Send a message via Telegram bot."""
        if not self.bot_token:
            return {"success": False, "error": "Bot token not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": parse_mode
                    }
                )
                data = response.json()
                if data.get("ok"):
                    return {"success": True, "message_id": data["result"]["message_id"]}
                return {"success": False, "error": data.get("description", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_updates(self, offset: int = 0, limit: int = 100) -> dict:
        """Get updates from Telegram."""
        if not self.bot_token:
            return {"success": False, "error": "Bot token not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/getUpdates",
                    params={"offset": offset, "limit": limit}
                )
                data = response.json()
                if data.get("ok"):
                    return {"success": True, "updates": data["result"]}
                return {"success": False, "error": data.get("description")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def set_webhook(self, url: str) -> dict:
        """Set webhook for receiving updates."""
        if not self.bot_token:
            return {"success": False, "error": "Bot token not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/setWebhook",
                    json={"url": url}
                )
                data = response.json()
                return {"success": data.get("ok", False), "result": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def verify_connection(self) -> bool:
        """Verify bot token is valid."""
        if not self.bot_token:
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/getMe")
                data = response.json()
                return data.get("ok", False)
        except Exception:
            return False
