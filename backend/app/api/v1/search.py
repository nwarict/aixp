from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])
search_service = SearchService()

@router.get("")
async def universal_search(
    q: str = Query(..., min_length=1),
    entity_types: Optional[List[str]] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = await search_service.search(
        query=q,
        tenant_id=current_user.tenant_id,
        db=db,
        entity_types=entity_types,
        limit=limit
    )
    return results
