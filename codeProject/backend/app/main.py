from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api.v1.api import api_router
from app.api.endpoints.admin import router as admin_router
from app.core.config import settings
from app.core.database import database
from app.core.middleware import TelegramWebAppMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запуск приложения
    print("Starting application...")
    await database.connect()
    yield
    # Завершение работы
    print("Shutting down application...")
    await database.disconnect()

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
    allow_origins=settings.ALLOWED_ORIGINS,
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
async def root():
    return {
        "message": "Restaurant Telegram Mini App API",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.DEBUG else None
    }

@app.get("/health")
async def health_check():
    """Endpoint для проверки здоровья сервиса"""
    db_status = "connected" if database.is_connected else "disconnected"
    return {
        "status": "healthy",
        "service": "restaurant-telegram-api",
        "database": db_status,
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