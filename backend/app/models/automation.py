from sqlalchemy import String, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Automation(BaseModel):
    __tablename__ = "automations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="inactive")
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_config: Mapped[dict] = mapped_column(JSON, default=dict)
    conditions: Mapped[list] = mapped_column(JSON, default=list)
    actions: Mapped[list] = mapped_column(JSON, default=list)
    flow_data: Mapped[dict] = mapped_column(JSON, default=dict)
    execution_count: Mapped[int] = mapped_column(default=0)
    last_executed_at: Mapped[str] = mapped_column(String(50), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    error_count: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str] = mapped_column(Text, nullable=True)
