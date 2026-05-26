"""
GovernAI Studio — Database Connection (Neon PostgreSQL Free Tier)
Async SQLAlchemy with connection pooling.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

engine = None
async_session_factory = None


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def init_db():
    """Initialize database engine and session factory."""
    global engine, async_session_factory
    settings = get_settings()

    # Strip ssl/sslmode from URL (we pass it via connect_args instead)
    db_url = settings.DATABASE_URL
    db_url = db_url.replace("?sslmode=require", "").replace("?ssl=require", "")
    db_url = db_url.replace("&sslmode=require", "").replace("&ssl=require", "")

    import ssl as ssl_module
    ssl_ctx = ssl_module.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl_module.CERT_NONE

    engine = create_async_engine(
        db_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,       # Detect stale connections before use
        pool_recycle=300,          # Recycle connections every 5 min (Neon drops idle)
        echo=settings.DEBUG,
        connect_args={"ssl": ssl_ctx},
    )

    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


async def close_db():
    """Close database engine."""
    global engine
    if engine:
        await engine.dispose()


async def get_db() -> AsyncSession:
    """Dependency: yields a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
