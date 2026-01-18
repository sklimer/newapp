#!/usr/bin/env python3
"""
Скрипт для запуска Telegram-бота
"""
import asyncio
import logging
import sys

from codeProject.backend.app.core.bot.telegram_bot import main as run_bot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting Telegram Bot...")
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Shutting down bot...")
        sys.exit(0)