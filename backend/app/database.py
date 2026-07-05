from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base for models
Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database init failed: {e}")
