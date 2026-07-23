import httpx
import hmac
import hashlib
from typing import Optional
from app.core.config import get_settings
from app.connectors.base import BaseConnector

settings = get_settings()

class WordPressConnector(BaseConnector):
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.site_url = config.get("site_url", "")
        self.api_key = config.get("api_key", "")
        self.webhook_secret = config.get("webhook_secret") or settings.wp_webhook_secret

    async def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify WordPress webhook signature."""
        if not self.webhook_secret:
            return True
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def send_to_wordpress(self, endpoint: str, data: dict) -> dict:
        """Send data to WordPress REST API."""
        if not self.site_url:
            return {"success": False, "error": "WordPress site URL not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.site_url}/wp-json/aixp/v1/{endpoint}",
                    json=data,
                    headers={"X-API-Key": self.api_key} if self.api_key else {}
                )
                return {
                    "success": 200 <= response.status_code < 300,
                    "status_code": response.status_code,
                    "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def verify_connection(self) -> bool:
        """Verify WordPress connection."""
        if not self.site_url:
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.site_url}/wp-json/")
                return response.status_code == 200
        except Exception:
            return False
