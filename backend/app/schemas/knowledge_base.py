from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class KnowledgeBaseCreate(BaseModel):
    title: str
    content: str
    content_type: str = "article"
    category: Optional[str] = None
    tags: List[str] = []
    language: str = "ar"
    is_published: bool = True

class KnowledgeBaseUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None

class KnowledgeBaseResponse(BaseModel):
    id: str
    title: str
    content: str
    content_type: str
    category: Optional[str]
    tags: List[str]
    language: str
    is_published: bool
    view_count: int
    helpful_count: int
    created_at: datetime
    tenant_id: str

    class Config:
        from_attributes = True

class KnowledgeBaseSearch(BaseModel):
    query: str
    limit: int = 5
