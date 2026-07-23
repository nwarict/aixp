from sqlalchemy import String, Boolean, JSON, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.models.base import BaseModel

class KnowledgeBase(BaseModel):
    __tablename__ = "knowledge_base"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), default="article")
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    source: Mapped[str] = mapped_column(String(255), nullable=True)
    file_type: Mapped[str] = mapped_column(String(50), nullable=True)
    file_size: Mapped[int] = mapped_column(default=0)
    language: Mapped[str] = mapped_column(String(10), default="ar")
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    view_count: Mapped[int] = mapped_column(default=0)
    helpful_count: Mapped[int] = mapped_column(default=0)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    embedding: Mapped[list] = mapped_column(Vector(1536), nullable=True)

    __table_args__ = (
        Index('ix_kb_embedding', 'embedding', postgresql_using='ivfflat'),
        Index('ix_kb_search', 'title', 'content', postgresql_using='gin'),
    )
