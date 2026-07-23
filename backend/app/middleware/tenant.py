from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from app.models.tenant import Tenant

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Tenant).where(Tenant.id == tenant_id, Tenant.is_active == True))
                tenant = result.scalar_one_or_none()
                if tenant:
                    request.state.tenant_id = tenant_id
                    request.state.tenant = tenant
        response = await call_next(request)
        return response
