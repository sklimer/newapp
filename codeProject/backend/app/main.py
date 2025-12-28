from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from .core.config import settings
from .core.database import database
from .core.middleware import TelegramWebAppMiddleware
import uvicorn
from app.api.endpoints.admin import router as admin_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Restaurant Telegram Mini App API",
    description="Backend API for Telegram mini app with payment integration for restaurants",
    version="1.0.0"
)

# Add Telegram Web App middleware first
app.add_middleware(TelegramWebAppMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Include API router


# Подключаем статические файлы и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем маршруты
app.include_router(api_router, prefix="/api/v1")
app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)