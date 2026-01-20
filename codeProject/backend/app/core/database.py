import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

Base = declarative_base()

# SQLAlchemy sync engine (синхронный движок)
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,  # Размер пула соединений
    max_overflow=30,  # Максимальное количество соединений сверх pool_size
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,  # Пересоздание соединений каждый час
    echo=False  # Логирование SQL запросов (True для отладки)
)

# Sync session maker (синхронная фабрика сессий)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# Функция для получения сессии БД
def get_db():
    """
    Создает и возвращает сессию базы данных.
    Используется как dependency в FastAPI.

    Пример использования в FastAPI:
    @app.get("/items")
    def read_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


# Функция для создания всех таблиц (для миграций/инициализации)
def create_tables():
    """
    Создает все таблицы в базе данных.
    Вызывается при инициализации приложения.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


# Утилитарные функции
def get_db_session():
    """Получение сессии для прямого использования (не через dependency injection)"""
    return SessionLocal()


def close_db_session(db):
    """Закрытие сессии"""
    if db:
        db.close()