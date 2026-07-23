from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LeadCreate(BaseModel):
    customer_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str = "new"
    priority: str = "medium"
    value: float = 0.0
    currency: str = "SAR"
    source: str = "manual"
    assigned_to: Optional[str] = None
    expected_close_date: Optional[str] = None
    custom_fields: dict = {}

class LeadUpdate(BaseModel):
    customer_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    assigned_to: Optional[str] = None
    expected_close_date: Optional[str] = None
    custom_fields: Optional[dict] = None

class LeadResponse(BaseModel):
    id: str
    customer_id: Optional[str]
    title: str
    description: Optional[str]
    status: str
    priority: str
    value: float
    currency: str
    source: str
    assigned_to: Optional[str]
    ai_score: float
    created_at: datetime
    updated_at: datetime
    tenant_id: str

    class Config:
        from_attributes = True
