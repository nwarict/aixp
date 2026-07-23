from sqlalchemy import String, Boolean, JSON, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from app.models.base import BaseModel

class Campaign(BaseModel):
    __tablename__ = "campaigns"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), default="broadcast")
    channel: Mapped[str] = mapped_column(String(50), default="email")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    content: Mapped[str] = mapped_column(Text, nullable=True)
    template_id: Mapped[str] = mapped_column(String(36), nullable=True)
    audience_type: Mapped[str] = mapped_column(String(50), default="all")
    audience_segment: Mapped[dict] = mapped_column(JSON, default=dict)
    audience_manual: Mapped[list] = mapped_column(ARRAY(String), default=list)
    scheduled_at: Mapped[str] = mapped_column(String(50), nullable=True)
    started_at: Mapped[str] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[str] = mapped_column(String(50), nullable=True)
    total_recipients: Mapped[int] = mapped_column(default=0)
    sent_count: Mapped[int] = mapped_column(default=0)
    delivered_count: Mapped[int] = mapped_column(default=0)
    read_count: Mapped[int] = mapped_column(default=0)
    failed_count: Mapped[int] = mapped_column(default=0)
    reply_count: Mapped[int] = mapped_column(default=0)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
