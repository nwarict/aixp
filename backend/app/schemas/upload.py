from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UploadResponse(BaseModel):
    id: str
    filename: str
    url: str
    size: int
    content_type: str
    created_at: datetime

    class Config:
        from_attributes = True
