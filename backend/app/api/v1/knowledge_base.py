from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse, KnowledgeBaseSearch
from app.services.ai_service import AIService

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])
ai_service = AIService()

@router.post("", response_model=KnowledgeBaseResponse)
async def create_article(
    data: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    article = KnowledgeBase(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **data.model_dump()
    )

    try:
        embedding = await ai_service.generate_embedding(data.content)
        article.embedding = embedding
    except:
        pass

    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article

@router.get("", response_model=list[KnowledgeBaseResponse])
async def list_articles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    query = select(KnowledgeBase).where(
        KnowledgeBase.tenant_id == current_user.tenant_id,
        KnowledgeBase.is_deleted == False
    )

    if category:
        query = query.where(KnowledgeBase.category == category)
    if search:
        query = query.where(
            KnowledgeBase.title.ilike(f"%{search}%") |
            KnowledgeBase.content.ilike(f"%{search}%")
        )

    query = query.order_by(desc(KnowledgeBase.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{article_id}", response_model=KnowledgeBaseResponse)
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == article_id,
            KnowledgeBase.tenant_id == current_user.tenant_id
        )
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.view_count += 1
    await db.commit()
    return article

@router.put("/{article_id}", response_model=KnowledgeBaseResponse)
async def update_article(
    article_id: str,
    data: KnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == article_id,
            KnowledgeBase.tenant_id == current_user.tenant_id
        )
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(article, field, value)

    if data.content:
        try:
            embedding = await ai_service.generate_embedding(data.content)
            article.embedding = embedding
        except:
            pass

    await db.commit()
    await db.refresh(article)
    return article

@router.delete("/{article_id}")
async def delete_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == article_id,
            KnowledgeBase.tenant_id == current_user.tenant_id
        )
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.is_deleted = True
    from datetime import datetime, timezone
    article.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Article deleted"}

@router.post("/{article_id}/helpful")
async def mark_helpful(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == article_id,
            KnowledgeBase.tenant_id == current_user.tenant_id
        )
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.helpful_count += 1
    await db.commit()
    return {"message": "Marked as helpful"}
