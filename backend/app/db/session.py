from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. ASYNC ENGINE (Cho FastAPI)
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 2. SYNC ENGINE (Cho Celery Worker)
# Worker cần session đồng bộ để tránh lỗi event loop phức tạp
sync_engine = create_engine(settings.SQLALCHEMY_SYNC_DATABASE_URI, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=sync_engine
)