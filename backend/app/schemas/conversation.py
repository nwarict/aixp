from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ConversationCreate(BaseModel):
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    channel: str
    subject: Optional[str] = None
    priority: str = "medium"
    ai_enabled: bool = True
    tags: List[str] = []

class ConversationUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    subject: Optional[str] = None
    ai_enabled: Optional[bool] = None
    tags: Optional[List[str]] = None

class ConversationResponse(BaseModel):
    id: str
    customer_id: Optional[str]
    contact_id: Optional[str]
    channel: str
    status: str
    priority: str
    assigned_to: Optional[str]
    subject: Optional[str]
    summary: Optional[str]
    ai_enabled: bool
    tags: List[str]
    last_message_at: Optional[str]
    created_at: datetime
    tenant_id: str

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    conversation_id: str
    content: str
    content_type: str = "text"
    attachments: List[dict] = []

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_type: str
    sender_id: Optional[str]
    content: str
    content_type: str
    is_ai_generated: bool
    is_read: bool
    created_at: datetime
    tenant_id: str

    class Config:
        from_attributes = True
