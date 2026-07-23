from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class AutomationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: dict = {}
    conditions: List[dict] = []
    actions: List[dict] = []
    flow_data: dict = {}

class AutomationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    trigger_config: Optional[dict] = None
    conditions: Optional[List[dict]] = None
    actions: Optional[List[dict]] = None
    flow_data: Optional[dict] = None

class AutomationResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    trigger_type: str
    trigger_config: dict
    conditions: List[dict]
    actions: List[dict]
    execution_count: int
    last_executed_at: Optional[str]
    created_at: datetime
    updated_at: datetime
    tenant_id: str

    class Config:
        from_attributes = True
