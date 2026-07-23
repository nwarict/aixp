from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseConnector(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "")
        self.type = config.get("type", "")
        self.provider = config.get("provider", "")

    @abstractmethod
    async def send_message(self, recipient: str, content: str, **kwargs) -> Dict:
        pass

    @abstractmethod
    async def receive_message(self, payload: Dict) -> Dict:
        pass

    @abstractmethod
    async def verify_webhook(self, request_data: Dict) -> bool:
        pass

    def get_webhook_url(self, base_url: str, connector_id: str) -> str:
        return f"{base_url}/api/v1/connectors/{connector_id}/webhook"
