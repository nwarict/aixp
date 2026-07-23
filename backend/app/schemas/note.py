from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NoteCreate(BaseModel):
    title: Optional[str] = None
    content: str
    related_type: str
    related_id: str
    is_private: bool = False
    attachments: List[dict] = []

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_private: Optional[bool] = None
    attachments: Optional[List[dict]] = None

class NoteResponse(BaseModel):
    id: str
    title: Optional[str]
    content: str
    related_type: str
    related_id: str
    created_by: str
    is_private: bool
    attachments: List[dict]
    created_at: datetime
    updated_at: datetime
    tenant_id: str

    class Config:
        from_attributes = True
