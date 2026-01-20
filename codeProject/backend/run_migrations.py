#!/usr/bin/env python
# run_migrations.py
import os
import sys
import logging
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect


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

    # Шаг 2: Создание подключения к базе данных
    logger.info("Шаг 2: Создание подключения к базе данных")
    try:
        engine = create_engine(database_url)
        logger.info("Подключение к базе данных успешно установлено")
    except Exception as e:
        logger.error(f"Ошибка при создании подключения к базе данных: {str(e)}")
        sys.exit(1)

    # Шаг 3: Подсчет количества таблиц в базе данных
    logger.info("Шаг 3: Подсчет количества таблиц в базе данных")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        table_count = len(tables)
        logger.info(f"Количество таблиц в базе данных: {table_count}")

        if table_count == 0:
            logger.info("База данных пуста - необходимо создать и применить миграции")
        else:
            logger.info(f"Обнаружены следующие таблицы: {tables}")
    except Exception as e:
        logger.error(f"Ошибка при получении списка таблиц из базы данных: {str(e)}")
        sys.exit(1)

    # Шаг 4: Загрузка конфигурации Alembic
    logger.info("Шаг 4: Загрузка конфигурации Alembic")
    try:
        alembic_cfg = Config("alembic.ini")
        logger.info("Конфигурация Alembic успешно загружена")
    except Exception as e:
        logger.error(f"Ошибка при загрузке конфигурации Alembic: {str(e)}")
        sys.exit(1)

    # Шаг 5: Установка URL базы данных в конфиг
    logger.info("Шаг 5: Установка URL базы данных в конфигурацию Alembic")
    try:
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        logger.info("URL базы данных успешно установлен в конфигурацию")
    except Exception as e:
        logger.error(f"Ошибка при установке URL базы данных: {str(e)}")
        sys.exit(1)

    # Шаг 6: Проверка наличия миграций и их создание при необходимости
    logger.info("Шаг 6: Проверка наличия миграций")
    versions_dir = os.path.join(os.path.dirname(alembic_cfg.config_file_name), "versions")
    if os.path.exists(versions_dir) and os.listdir(versions_dir):
        logger.info("Обнаружены существующие миграции")
    else:
        logger.info("Миграции не найдены - создание начальной миграции")
        try:
            logger.info("Создание новой миграции...")
            command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
            logger.info("Начальная миграция создана успешно")
        except Exception as e:
            logger.error(f"Ошибка при создании начальной миграции: {str(e)}")
            sys.exit(1)

    # Шаг 7: Получение текущей версии миграции
    logger.info("Шаг 7: Определение текущей версии миграции")
    try:
        from alembic.runtime.environment import EnvironmentContext
        from alembic.script import ScriptDirectory

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

    # Шаг 8: Выполнение миграции
    logger.info("Шаг 8: Начало выполнения миграций до последней версии")
    try:
        logger.info("Выполнение команды upgrade до версии 'head'...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Миграции успешно выполнены до последней версии")
    except Exception as e:
        logger.error(f"Ошибка при выполнении миграций: {str(e)}")
        sys.exit(1)

    # Шаг 9: Проверка количества таблиц после миграции
    logger.info("Шаг 9: Проверка количества таблиц в базе данных после миграции")
    try:
        inspector = inspect(engine)
        tables_after = inspector.get_table_names()
        table_count_after = len(tables_after)
        logger.info(f"Количество таблиц в базе данных после миграции: {table_count_after}")

        if table_count_after > table_count:
            logger.info(f"Количество новых таблиц после миграции: {table_count_after - table_count}")
            logger.info(f"Новые таблицы: {[table for table in tables_after if table not in tables]}")
        else:
            logger.info("Количество таблиц не изменилось после миграции")
    except Exception as e:
        logger.error(f"Ошибка при получении списка таблиц после миграции: {str(e)}")
        # Не завершаем программу аварийно, так как миграции уже выполнены

    # Шаг 10: Завершение
    logger.info("Шаг 10: Процесс миграции завершен успешно")
    logger.info("Все модели мигрированы в соответствии с доступными миграциями")


if __name__ == "__main__":
    setup_logging()
    run_migrations()