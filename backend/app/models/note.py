from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Note(BaseModel):
    __tablename__ = "notes"

    title: Mapped[str] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    related_type: Mapped[str] = mapped_column(String(50), nullable=False)
    related_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    is_private: Mapped[bool] = mapped_column(default=False)
    attachments: Mapped[list] = mapped_column(JSON, default=list)
