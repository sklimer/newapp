import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.api.v1.api import api_router
from app.api.endpoints.admin import router as admin_router
from app.core.config import settings
from app.core.database import async_engine
from app.core.middleware import TelegramWebAppMiddleware
from app.core.security import get_or_create_user_from_telegram
from app.api.deps import get_db



# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Create async session maker for lifespan
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запуск приложения
    logging.info("Starting application...")
    # We're not using the database connection in lifespan since it's handled by dependency injection
    yield
    # Завершение работы
    logging.info("Shutting down application...")
    # Close engine when shutting down
    await async_engine.dispose()

# Создание экземпляра FastAPI с lifespan
app = FastAPI(
    title="Restaurant Telegram Mini App API",
    description="Backend API for Telegram mini app with payment integration for restaurants",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Middleware
# 1. Telegram Web App middleware (первый, чтобы обрабатывать входящие запросы)
app.add_middleware(TelegramWebAppMiddleware)

# 2. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(api_router, prefix="/api/v1")
app.include_router(admin_router)

# Подключение статических файлов (если нужно)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Корневой endpoint для проверки здоровья
@app.get("/")
async def root(request: Request, db: AsyncSession = Depends(get_db)):
    # Проверяем, есть ли пользователь Telegram, и добавляем его при необходимости
    print('DEBUG: сработал @app.get("/")')  # Дополнительный дебаг-лог
    logger.info('сработал @app.get("/")')
    try:
        user = await get_or_create_user_from_telegram(request, db)
        user_authenticated = user is not None
        user_id = user.id if user else None
    except Exception as e:
        logger.error(f"Error in get_or_create_user_from_telegram: {e}")
        user_authenticated = False
        user_id = None

    return {
        "message": "Restaurant Telegram Mini App API",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.DEBUG else None,
        "user_authenticated": user_authenticated,
        "user_id": user_id
    }

@app.get("/health")
async def health_check():
    """Endpoint для проверки здоровья сервиса"""
    # In the async approach, we don't track connection status the same way
    return {
        "status": "healthy",
        "service": "restaurant-telegram-api",
        "database": "async_engine_ready",  # Simplified for async approach
        "debug": settings.DEBUG
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )