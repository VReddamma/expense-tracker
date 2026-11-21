from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

# Create database engine
engine = create_async_engine(
    settings.DATABASE_URL, echo=settings.DEBUG, pool_pre_ping=True
)


# Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
