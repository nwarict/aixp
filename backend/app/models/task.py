from sqlalchemy import String, Boolean, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Task(BaseModel):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="todo")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    assigned_to: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    related_type: Mapped[str] = mapped_column(String(50), nullable=True)
    related_id: Mapped[str] = mapped_column(String(36), nullable=True)
    due_date: Mapped[str] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[str] = mapped_column(String(50), nullable=True)
    reminders: Mapped[list] = mapped_column(JSON, default=list)
    custom_fields: Mapped[dict] = mapped_column(JSON, default=dict)
