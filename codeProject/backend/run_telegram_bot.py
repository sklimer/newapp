#!/usr/bin/env python3
"""
Скрипт для запуска Telegram-бота
"""
import asyncio
import logging
import sys
from threading import Thread

from app.core.telegram_bot import main as run_bot
from app.main import app
import uvicorn

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_fastapi():
    """Запуск FastAPI приложения"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


async def run_both():
    """Асинхронная функция для запуска обоих приложений"""
    # Запуск FastAPI в отдельном потоке
    fastapi_thread = Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    logger.info("FastAPI started in background thread")
    
    # Запуск Telegram-бота
    await run_bot()


if __name__ == "__main__":
    logger.info("Starting both FastAPI and Telegram Bot...")
    try:
        asyncio.run(run_both())
    except KeyboardInterrupt:
        logger.info("Shutting down applications...")
        sys.exit(0)