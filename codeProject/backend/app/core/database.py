import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

Base = declarative_base()

# SQLAlchemy sync engine (синхронный движок)
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,  # Размер пула соединений
    max_overflow=10,  # Максимальное количество соединений сверх pool_size
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=300,  # Пересоздание соединений каждые 5 минут
    pool_timeout=20,  # Таймаут ожидания соединения
    echo=False  # Логирование SQL запросов (True для отладки)
)

# SQLAlchemy async engine (асинхронный движок)
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=20,
    echo=False
)

# Sync session maker (синхронная фабрика сессий)
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False
)

# Async session maker (асинхронная фабрика сессий)
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    bind=async_engine,
    expire_on_commit=False
)

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# Функция для получения сессии БД (синхронной)
def get_db():
    """
    Создает и возвращает синхронную сессию базы данных.
    Используется как dependency в FastAPI для синхронных операций.

    Пример использования в FastAPI:
    @app.get("/items")
    def read_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


# Асинхронная функция для получения сессии БД
async def get_async_db():
    """
    Создает и возвращает асинхронную сессию базы данных.
    Используется как dependency в FastAPI для асинхронных операций.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Async database error: {e}")
            raise


# Функция для создания всех таблиц (для миграций/инициализации)
def create_tables():
    """
    Создает все таблицы в базе данных.
    Вызывается при инициализации приложения.
    """
    Base.metadata.create_all(bind=sync_engine)
    logger.info("Database tables created successfully")


# Утилитарные функции
def get_db_session():
    """Получение сессии для прямого использования (не через dependency injection)"""
    return SyncSessionLocal()


def close_db_session(db):
    """Закрытие сессии"""
    if db:
        db.close()