from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings
from sqlalchemy.orm import declarative_base
Base = declarative_base()
# Async database connection
database = Database(settings.DATABASE_URL)

# SQLAlchemy engine and metadata
engine = create_engine(settings.DATABASE_URL)
metadata = MetaData()

# Async session maker
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session