from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.ai import AIChatRequest, AIChatResponse, AIConfigUpdate
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])
ai_service = AIService()

@router.post("/chat", response_model=AIChatResponse)
async def chat(
    request: AIChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await ai_service.chat(
            message=request.message,
            tenant_id=current_user.tenant_id,
            conversation_id=request.conversation_id,
            context=request.context,
            use_knowledge=request.use_knowledge,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 2048,
            model=request.model,
            db=db
        )
        return AIChatResponse(
            response=result["response"],
            conversation_id=request.conversation_id or "",
            model_used=result["model_used"],
            confidence=result["confidence"],
            sources=result.get("sources", []),
            prompt_tokens=result.get("prompt_tokens", 0),
            completion_tokens=result.get("completion_tokens", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models(current_user: User = Depends(get_current_user)):
    """List available AI models from Ollama."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ai_service.ollama_host}/api/tags", timeout=10.0)
            data = response.json()
            return {"models": [m["name"] for m in data.get("models", [])]}
    except Exception as e:
        return {"models": [ai_service.default_model], "error": str(e)}

@router.post("/config")
async def update_ai_config(
    config: AIConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await db.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    for field, value in config.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)

    await db.commit()
    return {"message": "AI configuration updated"}

@router.get("/config")
async def get_ai_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "ai_model": tenant.ai_model,
        "ai_temperature": tenant.ai_temperature,
        "ai_max_tokens": tenant.ai_max_tokens,
        "ai_system_prompt": tenant.ai_system_prompt,
        "ai_knowledge_enabled": tenant.ai_knowledge_enabled,
        "ai_safety_rules": tenant.ai_safety_rules
    }
