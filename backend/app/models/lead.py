from sqlalchemy import String, Float, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Lead(BaseModel):
    __tablename__ = "leads"

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="new")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    value: Mapped[float] = mapped_column(default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="SAR")
    source: Mapped[str] = mapped_column(String(50), default="manual")
    assigned_to: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    expected_close_date: Mapped[str] = mapped_column(String(50), nullable=True)
    custom_fields: Mapped[dict] = mapped_column(JSON, default=dict)
    ai_score: Mapped[float] = mapped_column(default=0.0)
    ai_insights: Mapped[str] = mapped_column(Text, nullable=True)
