from sqlalchemy import String, Boolean, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from app.models.base import BaseModel

class Conversation(BaseModel):
    __tablename__ = "conversations"

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    contact_id: Mapped[str] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    assigned_to: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_model: Mapped[str] = mapped_column(String(100), nullable=True)
    tags: Mapped[list] = mapped_column(ARRAY(String), default=list)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    last_message_at: Mapped[str] = mapped_column(String(50), nullable=True)
    resolved_at: Mapped[str] = mapped_column(String(50), nullable=True)
    satisfaction_score: Mapped[int] = mapped_column(default=0)

    __table_args__ = (
        Index('ix_conversations_channel_status', 'channel', 'status'),
        Index('ix_conversations_assigned', 'assigned_to', 'status'),
    )
