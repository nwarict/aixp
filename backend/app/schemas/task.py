from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    assigned_to: Optional[str] = None
    related_type: Optional[str] = None
    related_id: Optional[str] = None
    due_date: Optional[str] = None
    reminders: List[dict] = []
    custom_fields: dict = {}

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    completed_at: Optional[str] = None
    custom_fields: Optional[dict] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    assigned_to: Optional[str]
    related_type: Optional[str]
    related_id: Optional[str]
    due_date: Optional[str]
    completed_at: Optional[str]
    created_at: datetime
    updated_at: datetime
    tenant_id: str

    class Config:
        from_attributes = True
