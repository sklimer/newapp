# run_migrations.py
import os
import sys
from alembic.config import Config
from alembic import command


def run_migrations():
    # Получаем URL базы данных из переменных окружения
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("DATABASE_URL environment variable is not set")
        sys.exit(1)

    # Создаем конфиг для Alembic
    alembic_cfg = Config("alembic.ini")

    # Устанавливаем URL базы данных в конфиг
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    print("Running database migrations...")
    # Выполняем миграции до последней версии
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    run_migrations()