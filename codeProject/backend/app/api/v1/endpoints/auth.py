import logging
import hashlib
import hmac
import json
from urllib.parse import parse_qs, unquote
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import get_or_create_user_from_telegram
from app.models.users import User
from app.schemas.users import UserResponse

from app.core import settings

router = APIRouter()

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Конфигурация
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN  # Замените на ваш токен бота из @BotFather
INIT_DATA_EXPIRY_HOURS = 24  # Время жизни initData в часах


class TelegramInitDataValidator:
    """Класс для валидации Telegram initData"""

    @staticmethod
    def parse_init_data(init_data_str: str) -> Dict[str, Any]:
        """Парсинг строки initData"""
        try:
            # Декодируем строку
            parsed_data = parse_qs(init_data_str)
            result = {}

            for key, values in parsed_data.items():
                if not values:
                    continue

                value = values[0]

                # Парсим JSON для user, receiver, chat
                if key in ('user', 'receiver', 'chat'):
                    try:
                        result[key] = json.loads(unquote(value))
                    except (json.JSONDecodeError, TypeError):
                        result[key] = value
                elif key == 'auth_date':
                    result[key] = int(value)
                else:
                    result[key] = value

            return result
        except Exception as e:
            logger.error(f"Error parsing initData: {e}")
            raise ValueError(f"Invalid initData format: {str(e)}")

    @staticmethod
    def validate_signature(init_data_str: str, bot_token: str) -> bool:
        """
        Валидация подписи Telegram initData

        Алгоритм:
        1. Извлекаем параметр 'hash'
        2. Сортируем остальные параметры по алфавиту
        3. Формируем data_check_string в формате "key=value\n"
        4. Вычисляем HMAC-SHA256 подпись
        5. Сравниваем с полученным hash
        """
        try:
            # Разбираем параметры
            parsed = parse_qs(init_data_str, keep_blank_values=True)

            # Извлекаем hash
            if 'hash' not in parsed:
                return False

            received_hash = parsed['hash'][0]

            # Создаем data_check_string
            data_check_parts = []
            for key in sorted(parsed.keys()):
                if key == 'hash':
                    continue

                value = parsed[key][0]
                if value:
                    data_check_parts.append(f"{key}={value}")

            data_check_string = "\n".join(data_check_parts)

            # Вычисляем секретный ключ
            secret_key = hashlib.sha256(bot_token.encode()).digest()

            # Вычисляем HMAC-SHA256
            computed_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256
            ).hexdigest()

            # Сравниваем хеши
            return hmac.compare_digest(computed_hash, received_hash)

        except Exception as e:
            logger.error(f"Error validating signature: {e}")
            return False

    @staticmethod
    def validate_auth_date(auth_date: int, expiry_hours: int = 24) -> bool:
        """Проверяем, что данные не устарели"""
        try:
            auth_datetime = datetime.fromtimestamp(auth_date)
            expiry_datetime = auth_datetime + timedelta(hours=expiry_hours)
            return datetime.utcnow() <= expiry_datetime
        except Exception as e:
            logger.error(f"Error validating auth date: {e}")
            return False

    @classmethod
    def validate_init_data(cls, init_data_str: str, bot_token: str) -> Optional[Dict[str, Any]]:
        """Полная валидация initData"""
        try:
            # Парсим данные
            parsed_data = cls.parse_init_data(init_data_str)

            # Проверяем обязательные поля
            required_fields = ['hash', 'auth_date', 'user']
            for field in required_fields:
                if field not in parsed_data:
                    logger.warning(f"Missing required field: {field}")
                    return None

            # Проверяем подпись
            if not cls.validate_signature(init_data_str, bot_token):
                logger.warning("Invalid Telegram signature")
                return None

            # Проверяем время жизни
            if not cls.validate_auth_date(parsed_data['auth_date'], INIT_DATA_EXPIRY_HOURS):
                logger.warning("InitData expired")
                return None

            return parsed_data

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return None


def get_telegram_init_data(request: Request) -> Optional[str]:
    """Извлекает initData из запроса"""
    # Проверяем разные способы передачи initData

    # 1. Из заголовка Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("tma "):
        return auth_header[4:]  # Убираем "tma "

    # 2. Из query параметров
    init_data = request.query_params.get("tgWebAppData")
    if init_data:
        return init_data

    # 3. Из тела запроса (JSON)
    try:
        body = request.json()
        if isinstance(body, dict) and "initData" in body:
            return body["initData"]
    except:
        pass

    # 4. Из формы
    try:
        form_data = request.form()
        if "initData" in form_data:
            return form_data["initData"]
    except:
        pass

    logger.info("No initData found in request")
    return None


async def verify_telegram_init_data(request: Request) -> Dict[str, Any]:
    """Верифицирует initData и возвращает распарсенные данные"""
    # Получаем initData из запроса
    init_data_str = get_telegram_init_data(request)

    if not init_data_str:
        logger.warning("No initData provided")
        raise HTTPException(
            status_code=400,
            detail="Telegram initData is required"
        )

    # Валидируем initData
    validator = TelegramInitDataValidator()
    parsed_data = validator.validate_init_data(init_data_str, TELEGRAM_BOT_TOKEN)

    if not parsed_data:
        logger.warning("Invalid initData")
        raise HTTPException(
            status_code=401,
            detail="Invalid Telegram authentication data"
        )

    logger.info(f"Validated Telegram user: {parsed_data.get('user', {}).get('id')}")
    return parsed_data


@router.post("/verify-telegram")
async def verify_telegram_auth(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    Verify Telegram Web App initData and return user
    """
    logging.info("verify_telegram_auth endpoint called")

    # Верифицируем initData
    telegram_data = await verify_telegram_init_data(request)

    # Извлекаем данные пользователя
    user_data = telegram_data.get('user')
    if not user_data:
        raise HTTPException(
            status_code=400,
            detail="No user data in initData"
        )

    # Создаем или получаем пользователя
    user = await get_or_create_user_from_telegram(user_data, db)

    if not user:
        raise HTTPException(
            status_code=500,
            detail="Failed to create/get user"
        )

    logger.info(f"User verified: {user.id}")

    return {
        "success": True,
        "user": UserResponse.from_orm(user),
        "telegram_data": {
            "auth_date": telegram_data.get('auth_date'),
            "query_id": telegram_data.get('query_id'),
            "chat": telegram_data.get('chat')
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_from_telegram(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    Get current user from Telegram Web App data, creating if doesn't exist
    """
    logger.info("get_current_user_from_telegram endpoint called")

    # Верифицируем initData
    telegram_data = await verify_telegram_init_data(request)

    # Извлекаем данные пользователя
    user_data = telegram_data.get('user')
    if not user_data:
        raise HTTPException(
            status_code=400,
            detail="No user data in initData"
        )

    # Получаем или создаем пользователя
    user = await get_or_create_user_from_telegram(user_data, db)

    logger.info(f"get_current_user_from_telegram= {user.id}")

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="This application must be accessed through Telegram Web App with valid init data"
        )

    return UserResponse.from_orm(user)


# Альтернативный эндпоинт для совместимости
@router.get("/user")
async def get_telegram_user(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    Alternative endpoint for getting Telegram user (for compatibility with frontend)
    """
    return await get_current_user_from_telegram(request, db)