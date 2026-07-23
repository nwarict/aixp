from sqlalchemy import String, Float, JSON, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class Deal(BaseModel):
    __tablename__ = "deals"

    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    stage: Mapped[str] = mapped_column(String(50), default="discovery")
    value: Mapped[float] = mapped_column(default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="SAR")
    probability: Mapped[float] = mapped_column(default=0.0)
    assigned_to: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    start_date: Mapped[str] = mapped_column(String(50), nullable=True)
    end_date: Mapped[str] = mapped_column(String(50), nullable=True)
    custom_fields: Mapped[dict] = mapped_column(JSON, default=dict)
