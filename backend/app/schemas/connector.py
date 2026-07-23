from pydantic import BaseModel
from typing import Optional, Dict

class ConnectorCreate(BaseModel):
    name: str
    type: str
    provider: str
    config: dict = {}
    settings: dict = {}

class ConnectorUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    config: Optional[dict] = None
    settings: Optional[dict] = None

class ConnectorResponse(BaseModel):
    id: str
    name: str
    type: str
    provider: str
    status: str
    config: dict
    message_count: int
    last_used_at: Optional[str]
    created_at: str
    tenant_id: str

    class Config:
        from_attributes = True
