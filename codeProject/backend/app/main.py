import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from sqlalchemy.orm import sessionmaker, Session
from app.api.version_selector import register_api_versions, APIVersion
from app.core.config import settings
from app.core.database import engine
from app.core.middleware import TelegramWebAppMiddleware
from app.core.security import get_or_create_user_from_telegram
from app.api.deps import get_db

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Synchronous engine does not need special session maker for lifespan
# Using the existing SessionLocal from database module
from app.core.database import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запуск приложения
    logger.info("Starting application...")
    # We're not using the database connection in lifespan since it's handled by dependency injection
    yield
    # Завершение работы
    logger.info("Shutting down application...")
    # Close engine when shutting down
    engine.dispose()


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://newapp-c2js.onrender.com",  # Домен вашего frontend на Vercel
        "https://*.onrender.com",  # Для Preview-деплоев
        "https://newapp-six-green.vercel.app",  # Для Preview-деплоев
        "https://*.vercel.app",  # Для Preview-деплоев
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Подключение маршрутов
register_api_versions(app, enabled_versions=[APIVersion.V1, APIVersion.V2])


# Подключение статических файлов (если нужно)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Корневой endpoint для проверки здоровья


@app.get("/health")
async def health_check():
    """Endpoint для проверки здоровья сервиса"""
    # Health check for synchronous engine
    return {
        "status": "healthy",
        "service": "restaurant-telegram-api",
        "database": "sync_engine_ready",  # Updated for sync approach
        "debug": settings.DEBUG
    }


@app.get("/api/versions")
async def get_api_versions():
    """Return information about available API versions"""
    return {
        "versions": [
            {"version": "v1", "status": "stable", "path": "/api/v1"},
            {"version": "v2", "status": "stable", "path": "/api/v2"}
        ],
        "current_version": "v2",
        "default_version": "v1"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )