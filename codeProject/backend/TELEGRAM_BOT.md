# Telegram-бот для ресторана

## Описание

Telegram-бот предназначен для интеграции с рестораном через Telegram Mini App. При первом запуске бот сохраняет информацию о пользователе в базу данных.

## Функциональность

- При команде `/start` бот сохраняет информацию о пользователе в базу данных
- Сохраняемая информация:
  - telegram_id (обязательно)
  - username
  - first_name
  - last_name
  - language_code

## Установка и запуск

### Требования

- Python 3.8+
- PostgreSQL

### Установка зависимостей

```bash
pip install aiogram python-dotenv
```

### Конфигурация

Создайте файл `.env` в директории `/backend` со следующими переменными:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота_от_BotFather
DATABASE_URL=postgresql://postgres:admin@localhost/res_db
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:admin@localhost/res_db
SECRET_KEY=ваш_секретный_ключ
```

### Применение миграций

Перед запуском бота необходимо применить миграции к базе данных:

```bash
# Установите alembic если еще не установлен
pip install alembic

# Примените миграции
cd /path/to/backend
python -m alembic upgrade head
```

### Запуск бота

```bash
cd /path/to/backend
python start_bot.py
```

## Настройка бота в Telegram

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен бота
3. Добавьте токен в файл `.env`
4. Настройте бота для использования в Telegram Mini App (если требуется)

## Архитектура

- Бот использует библиотеку `aiogram` версии 3.x
- Информация о пользователях сохраняется в таблицу `users` в поле `language_code` и других
- Используется асинхронная работа с базой данных через SQLAlchemy