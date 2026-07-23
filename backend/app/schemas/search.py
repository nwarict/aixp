from pydantic import BaseModel
from typing import Optional, List

class SearchRequest(BaseModel):
    query: str
    entity_type: Optional[str] = None
    limit: int = 20
    filters: Optional[dict] = None

class SearchResult(BaseModel):
    id: str
    entity_type: str
    title: str
    content: Optional[str]
    score: float
    metadata: Optional[dict]
