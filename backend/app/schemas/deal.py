from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DealCreate(BaseModel):
    lead_id: Optional[str] = None
    customer_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str = "draft"
    stage: str = "discovery"
    value: float = 0.0
    currency: str = "SAR"
    probability: float = 0.0
    assigned_to: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    custom_fields: dict = {}

class DealUpdate(BaseModel):
    lead_id: Optional[str] = None
    customer_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    value: Optional[float] = None
    probability: Optional[float] = None
    assigned_to: Optional[str] = None
    custom_fields: Optional[dict] = None

class DealResponse(BaseModel):
    id: str
    lead_id: Optional[str]
    customer_id: Optional[str]
    title: str
    description: Optional[str]
    status: str
    stage: str
    value: float
    currency: str
    probability: float
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    tenant_id: str

    class Config:
        from_attributes = True
