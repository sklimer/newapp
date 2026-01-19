import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings
from sqlalchemy.orm import declarative_base
Base = declarative_base()


# SQLAlchemy async engine
async_engine = create_async_engine(settings.ASYNC_DATABASE_URL)

# Async session maker
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
logger = logging.getLogger(__name__)
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def get_db():
    # logger.info('async def get_db()')
    async with AsyncSessionLocal() as session:
        yield session