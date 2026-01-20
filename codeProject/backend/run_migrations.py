#!/usr/bin/env python
# run_migrations.py
import os
import sys
import logging
from alembic.config import Config
from alembic import command


def setup_logging():
    """Настройка логирования для миграций"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def run_migrations():
    """Выполнение миграций базы данных"""
    logger = logging.getLogger(__name__)

    logger.info("Начало процесса миграции базы данных")

    # Шаг 1: Проверка URL базы данных
    logger.info("Шаг 1: Проверка наличия DATABASE_URL")
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        logger.error("DATABASE_URL environment variable is not set")
        sys.exit(1)

    logger.info(f"DATABASE_URL найден: {database_url.replace('://', '://***:***@') if '@' in database_url else database_url}")

    # Шаг 2: Загрузка конфигурации Alembic
    logger.info("Шаг 2: Загрузка конфигурации Alembic")
    try:
        alembic_cfg = Config("alembic.ini")
        logger.info("Конфигурация Alembic успешно загружена")
    except Exception as e:
        logger.error(f"Ошибка при загрузке конфигурации Alembic: {str(e)}")
        sys.exit(1)

    # Шаг 3: Установка URL базы данных в конфиг
    logger.info("Шаг 3: Установка URL базы данных в конфигурацию Alembic")
    try:
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        logger.info("URL базы данных успешно установлен в конфигурацию")
    except Exception as e:
        logger.error(f"Ошибка при установке URL базы данных: {str(e)}")
        sys.exit(1)

    # Шаг 4: Получение текущей версии миграции
    logger.info("Шаг 4: Определение текущей версии миграции")
    try:
        from alembic.runtime.environment import EnvironmentContext
        from alembic.script import ScriptDirectory
        from sqlalchemy import create_engine

        engine = create_engine(database_url)
        script = ScriptDirectory.from_config(alembic_cfg)

        with engine.connect() as conn:
            context = EnvironmentContext(alembic_cfg, script)
            current_rev = None

            def get_current_revision(rev, context):
                nonlocal current_rev
                current_rev = rev
                return []

            with context.begin_transaction():
                context.run_env()
                context.get_context().get_current_revision(get_current_revision)

        logger.info(f"Текущая версия миграции: {current_rev if current_rev else 'отсутствует (база данных пуста)'}")
    except Exception as e:
        logger.warning(f"Не удалось определить текущую версию миграции: {str(e)}")

    # Шаг 5: Выполнение миграции
    logger.info("Шаг 5: Начало выполнения миграций до последней версии")
    try:
        logger.info("Выполнение команды upgrade до версии 'head'...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Миграции успешно выполнены до последней версии")
    except Exception as e:
        logger.error(f"Ошибка при выполнении миграций: {str(e)}")
        sys.exit(1)

    # Шаг 6: Завершение
    logger.info("Шаг 6: Процесс миграции завершен успешно")
    logger.info("Все модели мигрированы в соответствии с доступными миграциями")


if __name__ == "__main__":
    setup_logging()
    run_migrations()