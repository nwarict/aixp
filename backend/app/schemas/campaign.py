from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: str = "broadcast"
    channel: str = "email"
    content: Optional[str] = None
    audience_type: str = "all"
    audience_segment: dict = {}
    audience_manual: List[str] = []
    scheduled_at: Optional[str] = None
    settings: dict = {}

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    content: Optional[str] = None
    audience_type: Optional[str] = None
    scheduled_at: Optional[str] = None
    settings: Optional[dict] = None

class CampaignResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str
    channel: str
    status: str
    content: Optional[str]
    total_recipients: int
    sent_count: int
    delivered_count: int
    read_count: int
    failed_count: int
    created_at: datetime
    tenant_id: str

    class Config:
        from_attributes = True
