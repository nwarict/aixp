from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class CustomerCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: str
    company: Optional[str] = None
    title: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    language: str = "ar"
    tags: List[str] = []
    custom_fields: dict = {}
    source: str = "manual"

class CustomerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None
    status: Optional[str] = None

class CustomerResponse(BaseModel):
    id: str
    email: Optional[str]
    phone: Optional[str]
    full_name: str
    company: Optional[str]
    title: Optional[str]
    language: str
    tags: List[str]
    source: str
    status: str
    created_at: datetime
    updated_at: datetime
    tenant_id: str

    class Config:
        from_attributes = True

class ContactCreate(BaseModel):
    customer_id: str
    type: str
    value: str
    label: str = "primary"
    is_primary: bool = False

class ContactResponse(BaseModel):
    id: str
    customer_id: str
    type: str
    value: str
    label: str
    is_primary: bool
    is_verified: bool

    class Config:
        from_attributes = True
