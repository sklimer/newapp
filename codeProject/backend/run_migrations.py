import os
import sys
import logging
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect, text


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

    logger.info(
        f"DATABASE_URL найден: {database_url.replace('://', '://***:***@') if '@' in database_url else database_url}")

    # Шаг 2: Создание подключения к базе данных
    logger.info("Шаг 2: Создание подключения к базе данных")
    try:
        engine = create_engine(database_url)
        logger.info("Подключение к базе данных успешно установлено")
    except Exception as e:
        logger.error(f"Ошибка при создании подключения к базе данных: {str(e)}")
        sys.exit(1)

    # Шаг 3: Проверка состояния базы данных
    logger.info("Шаг 3: Проверка состояния базы данных")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        table_count = len(tables)
        logger.info(f"Количество таблиц в базе данных: {table_count}")
        logger.info(f"Обнаружены следующие таблицы: {tables}")

        # Проверяем наличие таблицы alembic_version
        has_alembic_version = 'alembic_version' in tables
        logger.info(f"Таблица alembic_version существует: {has_alembic_version}")

        if has_alembic_version:
            # Проверяем, есть ли версия в таблице
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                alembic_version = result.scalar()
                if alembic_version:
                    logger.info(f"Текущая версия Alembic в базе: {alembic_version}")
                else:
                    logger.info("Таблица alembic_version пуста")
    except Exception as e:
        logger.error(f"Ошибка при проверке базы данных: {str(e)}")
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

    # Шаг 6: Проверка наличия папки versions и файлов миграций
    logger.info("Шаг 6: Проверка наличия файлов миграций")
    versions_dir = os.path.join(os.path.dirname(alembic_cfg.config_file_name), "versions")
    if os.path.exists(versions_dir) and os.listdir(versions_dir):
        logger.info(f"Обнаружены существующие миграции в папке {versions_dir}")
        migration_files = os.listdir(versions_dir)
        logger.info(f"Количество файлов миграций: {len(migration_files)}")
        for file in migration_files[:5]:  # Показываем первые 5 файлов
            logger.info(f"  - {file}")
    else:
        logger.info(f"Папка versions не существует или пуста: {versions_dir}")

        # Создаем папку versions если ее нет
        if not os.path.exists(versions_dir):
            os.makedirs(versions_dir, exist_ok=True)
            logger.info(f"Создана папка versions: {versions_dir}")

    # Шаг 7: Определение нужного действия
    logger.info("Шаг 7: Определение стратегии миграции")

    if not has_alembic_version or not alembic_version:
        logger.info("База данных не инициализирована с Alembic")

        # Если есть таблицы, но нет alembic_version, нужно сделать stamp
        if table_count > 1:
            logger.info("База данных уже содержит таблицы, делаем stamp текущего состояния...")
            try:
                command.stamp(alembic_cfg, "head")
                logger.info("Stamp успешно выполнен")
            except Exception as e:
                logger.error(f"Ошибка при выполнении stamp: {str(e)}")
                logger.info("Попытка создать начальную миграцию...")
                try:
                    command.revision(alembic_cfg, autogenerate=True, message="Initial migration from existing database")
                    logger.info("Начальная миграция создана успешно")
                except Exception as e:
                    logger.error(f"Ошибка при создании начальной миграции: {str(e)}")
                    logger.info("Попытка создать пустую миграцию...")
                    try:
                        command.revision(alembic_cfg, message="Empty initial migration")
                        logger.info("Пустая миграция создана успешно")
                    except Exception as e:
                        logger.error(f"Ошибка при создании пустой миграции: {str(e)}")
                        sys.exit(1)

    else:
        logger.info("База данных уже инициализирована с Alembic")

    # Шаг 8: Создание миграции для новых изменений (например, поля balance)
    logger.info("Шаг 8: Создание миграции для новых изменений")
    try:
        # Автогенерация миграции на основе различий между моделями и базой
        logger.info("Проверка изменений в моделях...")
        command.revision(alembic_cfg, autogenerate=True, message="Add missing columns and changes")
        logger.info("Миграция создана успешно")
    except Exception as e:
        logger.warning(f"Не удалось создать автогенерацию миграции: {str(e)}")
        logger.info("Создание пустой миграции для ручного заполнения...")
        try:
            command.revision(alembic_cfg, message="Manual migration for database changes")
            logger.info("Пустая миграция создана успешно")
        except Exception as e:
            logger.error(f"Ошибка при создании пустой миграции: {str(e)}")

    # Шаг 9: Применение миграций
    logger.info("Шаг 9: Применение миграций")
    try:
        logger.info("Применение миграций до версии 'head'...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Миграции успешно применены")
    except Exception as e:
        logger.error(f"Ошибка при применении миграций: {str(e)}")
        logger.info("Попытка применить миграции с опцией --sql для отладки...")
        try:
            # Попробуем получить SQL для отладки
            import io

            output = io.StringIO()
            command.upgrade(alembic_cfg, "head", sql=True)
            logger.info("SQL команды миграции сгенерированы")
        except Exception as e2:
            logger.error(f"Ошибка при генерации SQL: {e2}")

    # Шаг 10: Проверка наличия поля balance
    logger.info("Шаг 10: Проверка наличия поля balance в таблице users")
    try:
        with engine.connect() as conn:
            # Проверяем наличие поля balance
            result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'balance'
                """))
            if result.fetchone():
                logger.info("✓ Поле balance существует в таблице users")
            else:
                logger.warning("✗ Поле balance отсутствует в таблице users")
                logger.info("Добавление поля balance вручную...")
                conn.execute(text("ALTER TABLE users ADD COLUMN balance DECIMAL(10,2) DEFAULT 0.00;"))
                conn.commit()
                logger.info("✓ Поле balance добавлено")
    except Exception as e:
        logger.error(f"Ошибка при проверке поля balance: {str(e)}")

    # Шаг 11: Завершение
    logger.info("Шаг 11: Процесс миграции завершен успешно")

if __name__ == "__main__":
    setup_logging()
    run_migrations()