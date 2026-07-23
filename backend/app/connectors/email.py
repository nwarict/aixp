import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.core.config import get_settings
from app.connectors.base import BaseConnector

settings = get_settings()

class EmailConnector(BaseConnector):
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.host = config.get("host") or settings.smtp_host
        self.port = config.get("port") or settings.smtp_port
        self.user = config.get("user") or settings.smtp_user
        self.password = config.get("password") or settings.smtp_password
        self.from_addr = config.get("from") or settings.smtp_from
        self.use_tls = config.get("tls", True)

    async def send_message(self, to: str, subject: str, body: str, html: str = None) -> dict:
        """Send an email message."""
        if not all([self.host, self.user, self.password]):
            return {"success": False, "error": "SMTP not configured"}

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_addr
            msg["To"] = to

            msg.attach(MIMEText(body, "plain", "utf-8"))
            if html:
                msg.attach(MIMEText(html, "html", "utf-8"))

            # Run SMTP in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._send_smtp_sync, msg, to
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_smtp_sync(self, msg, to):
        with smtplib.SMTP(self.host, self.port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.from_addr, [to], msg.as_string())
        return {"success": True, "message_id": None}

    async def send_bulk(self, recipients: List[str], subject: str, body: str) -> dict:
        """Send bulk emails."""
        results = []
        for recipient in recipients:
            result = await self.send_message(recipient, subject, body)
            results.append({"to": recipient, **result})
        return {"success": True, "results": results}

    async def verify_connection(self) -> bool:
        """Verify SMTP connection."""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._verify_smtp_sync)
        except Exception:
            return False

    def _verify_smtp_sync(self):
        with smtplib.SMTP(self.host, self.port, timeout=10) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.user, self.password)
            return True
