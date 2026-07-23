import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, JSON, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(50), default="free")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    branding: Mapped[dict] = mapped_column(JSON, default=dict)
    limits: Mapped[dict] = mapped_column(JSON, default=dict)
    ai_model: Mapped[str] = mapped_column(String(100), default="llama3.1:8b")
    ai_temperature: Mapped[float] = mapped_column(default=0.7)
    ai_max_tokens: Mapped[int] = mapped_column(default=2048)
    ai_system_prompt: Mapped[str] = mapped_column(Text, default="You are a helpful AI assistant.")
    ai_knowledge_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_safety_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
