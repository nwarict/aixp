from sqlalchemy import String, Boolean, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sender_id: Mapped[str] = mapped_column(String(36), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), default="text")
    attachments: Mapped[list] = mapped_column(JSON, default=list)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_confidence: Mapped[float] = mapped_column(default=0.0)
    ai_model: Mapped[str] = mapped_column(String(100), nullable=True)
    ai_prompt_tokens: Mapped[int] = mapped_column(default=0)
    ai_completion_tokens: Mapped[int] = mapped_column(default=0)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[str] = mapped_column(String(50), nullable=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=True)
    external_status: Mapped[str] = mapped_column(String(50), nullable=True)
