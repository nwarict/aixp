import httpx
import hmac
import hashlib
from typing import Optional, Dict
from app.core.config import get_settings
from app.connectors.base import BaseConnector

settings = get_settings()

class WebhookConnector(BaseConnector):
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.secret = config.get("secret", "")
        self.timeout = config.get("timeout", 30)

    async def send_webhook(self, url: str, payload: dict, headers: dict = None, sign: bool = True) -> dict:
        """Send webhook payload to URL."""
        try:
            request_headers = headers or {}
            request_headers["Content-Type"] = "application/json"

            if sign and self.secret:
                signature = self._generate_signature(payload)
                request_headers["X-Webhook-Signature"] = signature

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=request_headers)
                return {
                    "success": 200 <= response.status_code < 300,
                    "status_code": response.status_code,
                    "response": response.text[:1000]
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_signature(self, payload: dict) -> str:
        """Generate HMAC signature for webhook."""
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        return hmac.new(
            self.secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()

    def verify_signature(self, payload: dict, signature: str) -> bool:
        """Verify webhook signature."""
        if not self.secret:
            return True
        expected = self._generate_signature(payload)
        return hmac.compare_digest(expected, signature)

    async def verify_connection(self, url: str) -> bool:
        """Verify webhook endpoint is reachable."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                return True
        except Exception:
            return False
