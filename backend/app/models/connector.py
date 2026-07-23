from sqlalchemy import String, Boolean, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Connector(BaseModel):
    __tablename__ = "connectors"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="inactive")
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    webhook_url: Mapped[str] = mapped_column(String(500), nullable=True)
    webhook_secret: Mapped[str] = mapped_column(String(255), nullable=True)
    last_error: Mapped[str] = mapped_column(Text, nullable=True)
    last_used_at: Mapped[str] = mapped_column(String(50), nullable=True)
    message_count: Mapped[int] = mapped_column(default=0)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
