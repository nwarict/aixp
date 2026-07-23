import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text, select
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database with required extensions and default data."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.create_all)

    # Create default tenant and admin user
    async with AsyncSessionLocal() as session:
        from app.models.tenant import Tenant
        from app.models.user import User
        from app.core.security import get_password_hash

        result = await session.execute(
            select(Tenant).where(Tenant.slug == "default")
        )
        if result.scalar_one_or_none() is None:
            default_tenant = Tenant(
                name="Default Organization",
                slug="default",
                plan="enterprise",
                settings={"language": "ar", "timezone": "Asia/Riyadh", "currency": "SAR"}
            )
            session.add(default_tenant)
            await session.flush()

            admin_user = User(
                email="admin@aixp.local",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role="superadmin",
                tenant_id=default_tenant.id,
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            print("✅ Default tenant and admin user created")
            print("   Admin: admin@aixp.local / admin123")
