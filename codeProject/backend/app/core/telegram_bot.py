import asyncio
import logging
from typing import Dict, Any, Optional
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.config import settings
from app.models.users import User
from app.core.database import async_session

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def save_user_to_database(user_data: Dict[str, Any]) -> User:
    """
    Сохраняет информацию о пользователе в базу данных
    """
    async with async_session() as session:
        # Проверяем, существует ли пользователь с таким telegram_id
        result = await session.execute(
            select(User).where(User.telegram_id == str(user_data.get("id")))
        )
        existing_user = result.scalars().first()
        
        if existing_user:
            # Обновляем данные существующего пользователя
            update_fields = {
                'username': user_data.get("username"),
                'first_name': user_data.get("first_name"),
                'last_name': user_data.get("last_name"),
                'language_code': user_data.get("language_code"),  # добавляем language_code если поддерживается
            }
            
            for field, value in update_fields.items():
                if value is not None and hasattr(existing_user, field):
                    setattr(existing_user, field, value)
            
            existing_user.updated_at = func.now()
            await session.commit()
            logger.info(f"Updated existing user with telegram_id: {user_data.get('id')}")
            return existing_user
        else:
            # Создаем нового пользователя
            new_user = User(
                telegram_id=str(user_data.get("id")),
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                language_code=user_data.get("language_code"),
                is_active=True
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            logger.info(f"Created new user with telegram_id: {user_data.get('id')}")
            return new_user

@dp.message(CommandStart())
async def handle_start(message: types.Message):
    """
    Обработчик команды /start - сохраняет информацию о пользователе в базу данных
    """
    try:
        # Получаем информацию о пользователе из сообщения
        user_info = {
            "id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "language_code": getattr(message.from_user, 'language_code', None),
        }
        
        logger.info(f"New user started the bot: {user_info}")
        
        # Сохраняем информацию о пользователе в базу данных
        saved_user = await save_user_to_database(user_info)
        
        # Отправляем приветственное сообщение
        welcome_message = (
            f"Привет, {saved_user.first_name or 'пользователь'}! "
            f"Ваша информация успешно сохранена в базе данных."
        )
        await message.answer(welcome_message)
        
    except Exception as e:
        logger.error(f"Error handling start command: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса.")

async def main():
    """
    Запуск бота
    """
    try:
        logger.info("Starting Telegram bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())