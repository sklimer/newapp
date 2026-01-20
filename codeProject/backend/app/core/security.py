import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Callable, Tuple
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps

from .config import settings
from .telegram import (
    validate_telegram_init_data,
    get_telegram_user_data,
    is_running_in_telegram_web_app
)

# Настройка логирования для этого модуля
logger = logging.getLogger(__name__)

# Инициализация HTTPBearer для JWT аутентификации
security = HTTPBearer(auto_error=False)


class AuthenticationError(Exception):
    """Кастомное исключение для ошибок аутентификации"""
    pass


class TokenValidationError(AuthenticationError):
    """Ошибка валидации токена"""
    pass


class TelegramAuthError(AuthenticationError):
    """Ошибка Telegram аутентификации"""
    pass


def verify_token(token: str) -> dict:
    """
    Проверяет JWT токен и возвращает payload

    Args:
        token: JWT токен

    Returns:
        dict: Декодированный payload токена

    Raises:
        HTTPException: Если токен невалидный или просрочен
    """
    logger.info(f"🔐 Начинаем проверку JWT токена. Длина токена: {len(token)} символов")

    try:
        # Декодируем токен
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )

        logger.info(f"✅ JWT токен успешно верифицирован. User ID: {payload.get('sub')}")
        logger.debug(f"🔐 Payload токена: {payload}")

        return payload

    except jwt.ExpiredSignatureError:
        logger.error("❌ JWT токен просрочен")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен авторизации истек. Пожалуйста, войдите снова.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except jwt.InvalidTokenError as e:
        logger.error(f"❌ Невалидный JWT токен: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Невалидный токен авторизации: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при проверке токена: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка при проверке авторизации"
        )


async def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Получает текущего пользователя из JWT токена

    Args:
        credentials: HTTP авторизационные данные

    Returns:
        str: ID пользователя из токена

    Raises:
        HTTPException: Если авторизация не удалась
    """
    logger.info("👤 Получение текущего пользователя из JWT токена")

    # Проверяем наличие credentials
    if not credentials:
        logger.warning("⚠️ Отсутствуют авторизационные данные")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        token = credentials.credentials
        logger.debug(f"🔐 Получен токен (первые 20 символов): {token[:20]}...")

        payload = verify_token(token)

        user_id = payload.get("sub")
        if not user_id:
            logger.error("❌ В токене отсутствует subject (sub)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не содержит идентификатора пользователя"
            )

        logger.info(f"✅ Пользователь аутентифицирован. User ID: {user_id}")
        return user_id

    except HTTPException:
        # Пробрасываем HTTP исключения дальше
        raise
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при получении пользователя: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке авторизации"
        )


def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создает JWT access токен

    Args:
        data: Данные для кодирования в токен
        expires_delta: Время жизни токена

    Returns:
        str: Закодированный JWT токен
    """
    logger.info(f"🔐 Создание access токена для данных: {list(data.keys())}")

    try:
        to_encode = data.copy()

        # Устанавливаем время истечения токена
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })

        # Кодируем токен
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        logger.info(f"✅ Access токен создан. Истекает: {expire}")
        logger.debug(f"🔐 Payload токена: {to_encode}")

        return encoded_jwt

    except Exception as e:
        logger.error(f"❌ Ошибка при создании токена: {str(e)}", exc_info=True)
        raise


# ИСПРАВЛЕННАЯ ВЕРСИЯ: Простая зависимость, а не фабрика
async def require_telegram_auth(request: Request) -> Dict[str, Any]:
    """
    Dependency для проверки, что запрос пришел из Telegram и валидации init data

    Args:
        request: FastAPI Request объект

    Returns:
        Dict[str, Any]: Данные пользователя из Telegram

    Raises:
        HTTPException: Если валидация не удалась
    """
    logger.info("🔍 Начинаем валидацию Telegram запроса")
    logger.debug(f"📡 Метод запроса: {request.method}")
    logger.debug(f"📡 URL запроса: {request.url}")
    logger.debug(f"📡 Заголовки: {dict(request.headers)}")

    try:
        # Проверяем, что запрос из Telegram Web App
        is_telegram = is_running_in_telegram_web_app(request)
        if not is_telegram:
            logger.warning("⚠️ Запрос не из Telegram Web App")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Данный запрос должен выполняться из Telegram Web App"
            )

        logger.info("✅ Запрос подтвержден как Telegram Web App")

        # Получаем init data из разных источников
        init_data = None
        sources = [
            ("header-x-telegram-web-app-init-data", request.headers.get("x-telegram-web-app-init-data")),
            ("header-X-Telegram-WebApp-InitData", request.headers.get("X-Telegram-WebApp-InitData")),
            ("query-param-initData", request.query_params.get("initData")),
        ]

        for source_name, data in sources:
            if data:
                init_data = data
                logger.info(f"📥 Найден initData в {source_name}")
                break

        if not init_data:
            # Пробуем получить из тела запроса
            try:
                body = await request.json()
                init_data = body.get("initData") or body.get("init_data")
                if init_data:
                    logger.info("📥 Найден initData в теле запроса (JSON)")
            except:
                pass

        if not init_data:
            logger.error("❌ initData не найден в запросе")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отсутствуют данные инициализации Telegram (initData). "
                       "Пожалуйста, отправьте initData в заголовке 'x-telegram-web-app-init-data' "
                       "или в параметре 'initData'"
            )

        logger.info(f"📥 Получен initData. Длина: {len(init_data)} символов")
        logger.debug(f"📥 initData (первые 200 символов): {init_data[:200]}...")

        # Валидируем init data
        try:
            validate_telegram_init_data(init_data)
            logger.info("✅ initData успешно верифицирован")
        except Exception as e:
            logger.error(f"❌ Ошибка валидации initData: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Невалидные данные Telegram: {str(e)}"
            )

        # Получаем данные пользователя
        user_data = get_telegram_user_data(init_data)
        if not user_data:
            logger.error("❌ Не удалось извлечь данные пользователя из initData")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось извлечь данные пользователя"
            )

        logger.info(f"✅ Данные пользователя получены. ID: {user_data.get('id')}")
        logger.debug(f"👤 Данные пользователя: {user_data}")

        return user_data

    except HTTPException:
        # Пробрасываем HTTP исключения дальше
        raise
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при валидации Telegram: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка при обработке Telegram аутентификации"
        )


# ИСПРАВЛЕННАЯ ВЕРСИЯ: Простая зависимость, а не фабрика
async def require_telegram_web_app(request: Request) -> bool:
    """
    Dependency для проверки, что запрос пришел из Telegram Web App

    Args:
        request: FastAPI Request объект

    Returns:
        bool: True если запрос из Telegram Web App

    Raises:
        HTTPException: Если запрос не из Telegram Web App
    """
    logger.info("🔍 Проверка окружения Telegram Web App")

    try:
        is_telegram = is_running_in_telegram_web_app(request)

        if not is_telegram:
            logger.warning("⚠️ Запрос не из Telegram Web App")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот эндпоинт доступен только из Telegram Web App"
            )

        logger.info("✅ Запрос подтвержден как Telegram Web App")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при проверке окружения Telegram: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при проверке окружения"
        )


def get_or_create_user_from_telegram_sync(
        telegram_user_data: Dict[str, Any],
        db: Session
) -> Optional[Any]:
    """
    Получает или создает пользователя на основе данных из Telegram

    Args:
        telegram_user_data: Данные пользователя из валидированного initData Telegram
        db: Сессия базы данных

    Returns:
        Optional[Any]: Объект пользователя или None в случае ошибки
    """
    logger.info("👤 Начинаем обработку пользователя из Telegram (синхронная версия)")

    # Проверяем входные данные
    if not telegram_user_data:
        logger.error("❌ Получены пустые данные пользователя Telegram")
        return None

    if 'id' not in telegram_user_data:
        logger.error("❌ В данных пользователя Telegram отсутствует поле 'id'")
        logger.debug(f"❌ Полученные данные: {telegram_user_data}")
        return None

    telegram_id = str(telegram_user_data['id'])
    logger.info(f"👤 Обработка пользователя Telegram с ID: {telegram_id}")

    try:
        # Импортируем модель здесь, чтобы избежать циклических импортов
        from app.models.users import User as UserModel

        # Извлекаем данные пользователя
        user_info = {
            'telegram_id': telegram_id,
            'first_name': telegram_user_data.get('first_name', ''),
            'last_name': telegram_user_data.get('last_name'),
            'username': telegram_user_data.get('username'),
            'photo_url': telegram_user_data.get('photo_url'),
            'language_code': telegram_user_data.get('language_code'),
            'is_premium': telegram_user_data.get('is_premium', False),
        }

        logger.debug(f"📋 Извлеченная информация о пользователе: {user_info}")

        # Проверяем существование пользователя
        db_user = db.query(UserModel).filter(
            UserModel.telegram_id == telegram_id
        ).first()

        if db_user:
            logger.info(f"👤 Пользователь с telegram_id={telegram_id} уже существует")
            return _update_existing_user(db_user, user_info, db)
        else:
            logger.info(f"👤 Создание нового пользователя с telegram_id={telegram_id}")
            return _create_new_user(user_info, db)

    except SQLAlchemyError as e:
        logger.error(f"❌ Ошибка базы данных при работе с пользователем: {str(e)}", exc_info=True)
        db.rollback()
        return None
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при работе с пользователем: {str(e)}", exc_info=True)
        db.rollback()
        return None


def _update_existing_user(
        user: Any,
        user_info: Dict[str, Any],
        db: Session
) -> Any:
    """
    Обновляет существующего пользователя

    Args:
        user: Объект пользователя
        user_info: Новые данные пользователя
        db: Сессия базы данных

    Returns:
        Any: Обновленный объект пользователя
    """
    logger.info(f"🔄 Обновление существующего пользователя ID={user.id}")

    updated_fields = []
    current_time = datetime.now(timezone.utc)

    # Поля для обновления
    fields_to_update = {
        'first_name': 'first_name',
        'last_name': 'last_name',
        'username': 'username',
        'photo_url': 'photo_url',
        'language_code': 'language_code',
        'is_premium': 'is_premium',
    }

    # Проверяем и обновляем поля
    for model_field, info_field in fields_to_update.items():
        new_value = user_info.get(info_field)
        current_value = getattr(user, model_field, None)

        # Проверяем, нужно ли обновлять поле
        if new_value is not None and new_value != current_value:
            setattr(user, model_field, new_value)
            updated_fields.append(model_field)
            logger.debug(f"   ↪️ Обновлено поле {model_field}: {current_value} → {new_value}")

    # Обновляем метаданные
    if updated_fields:
        user.updated_at = current_time
        user.last_login = current_time

        try:
            db.commit()
            db.refresh(user)
            logger.info(f"✅ Пользователь ID={user.id} успешно обновлен. Измененные поля: {updated_fields}")
        except Exception as e:
            logger.error(f"❌ Ошибка при сохранении обновлений пользователя: {str(e)}")
            db.rollback()
            raise
    else:
        # Обновляем только last_login
        user.last_login = current_time
        db.commit()
        logger.info(f"✅ Пользователь ID={user.id} без изменений, обновлено только last_login")

    return user


def _create_new_user(
        user_info: Dict[str, Any],
        db: Session
) -> Optional[Any]:
    """
    Создает нового пользователя

    Args:
        user_info: Данные пользователя
        db: Сессия базы данных

    Returns:
        Optional[Any]: Созданный объект пользователя или None
    """
    logger.info("🆕 Создание нового пользователя")

    try:
        from app.models.users import User as UserModel

        current_time = datetime.now(timezone.utc)

        # Генерируем реферальный код
        telegram_id = user_info['telegram_id']
        referral_code = f"REF{telegram_id[-6:].upper()}" if len(telegram_id) >= 6 else f"REF{telegram_id}"

        # Подготавливаем данные для создания
        create_data = {
            'telegram_id': user_info['telegram_id'],
            'first_name': user_info['first_name'],
            'last_name': user_info.get('last_name'),
            'username': user_info.get('username'),
            'photo_url': user_info.get('photo_url'),
            'language_code': user_info.get('language_code'),
            'is_premium': user_info.get('is_premium', False),
            'referral_code': referral_code,
            'last_login': current_time,
            'created_at': current_time,
            'updated_at': current_time,
        }

        # Удаляем None значения
        create_data = {k: v for k, v in create_data.items() if v is not None}

        logger.debug(f"📋 Данные для создания пользователя: {create_data}")

        # Создаем пользователя
        new_user = UserModel(**create_data)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"✅ Новый пользователь создан успешно. ID: {new_user.id}, Telegram ID: {telegram_id}")
        logger.info(f"✅ Реферальный код: {new_user.referral_code}")

        return new_user

    except Exception as e:
        logger.error(f"❌ Ошибка при создании пользователя: {str(e)}", exc_info=True)
        db.rollback()
        return None


# Декоратор для защиты эндпоинтов
def protected_endpoint(func: Callable):
    """
    Декоратор для защиты эндпоинтов JWT аутентификацией

    Args:
        func: Функция эндпоинта

    Returns:
        Callable: Обернутая функция
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"🛡️ Защищенный эндпоинт вызван: {func.__name__}")

        # Проверяем наличие пользователя в kwargs
        if 'current_user' not in kwargs:
            logger.error("❌ Эндпоинт не имеет параметра current_user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Конфигурационная ошибка эндпоинта"
            )

        user_id = kwargs['current_user']
        logger.info(f"👤 Авторизованный пользователь: {user_id}")

        return await func(*args, **kwargs)

    return wrapper


# Дополнительные утилиты
def create_telegram_token(telegram_user_data: Dict[str, Any]) -> str:
    """
    Создает JWT токен на основе данных пользователя Telegram

    Args:
        telegram_user_data: Данные пользователя из Telegram

    Returns:
        str: JWT токен
    """
    logger.info(f"🔐 Создание JWT токена для пользователя Telegram: {telegram_user_data.get('id')}")

    try:
        telegram_id = str(telegram_user_data.get('id'))

        token_data = {
            "sub": telegram_id,
            "telegram_id": telegram_id,
            "username": telegram_user_data.get('username'),
            "first_name": telegram_user_data.get('first_name'),
            "last_name": telegram_user_data.get('last_name'),
            "is_premium": telegram_user_data.get('is_premium', False),
        }

        # Удаляем None значения
        token_data = {k: v for k, v in token_data.items() if v is not None}

        token = create_access_token(token_data)

        logger.info(f"✅ JWT токен создан для telegram_id={telegram_id}")
        return token

    except Exception as e:
        logger.error(f"❌ Ошибка при создании Telegram токена: {str(e)}", exc_info=True)
        raise


async def get_telegram_user_or_create(
        request: Request,
        db: Session
) -> Tuple[Any, str]:
    """
    Получает пользователя Telegram или создает нового, возвращая также JWT токен

    Args:
        request: FastAPI Request
        db: Сессия базы данных

    Returns:
        Tuple[Any, str]: (объект пользователя, JWT токен)

    Raises:
        HTTPException: В случае ошибки аутентификации
    """
    logger.info("🔑 Комплексная аутентификация Telegram пользователя")

    try:
        # Получаем данные пользователя из Telegram
        telegram_user_data = await require_telegram_auth(request)

        # Получаем или создаем пользователя в БД
        user = get_or_create_user_from_telegram_sync(telegram_user_data, db)

        if not user:
            logger.error("❌ Не удалось получить или создать пользователя")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при работе с пользователем"
            )

        # Создаем JWT токен
        token = create_telegram_token(telegram_user_data)

        logger.info(f"✅ Пользователь аутентифицирован. User ID: {user.id}, Telegram ID: {telegram_user_data.get('id')}")

        return user, token

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка комплексной аутентификации: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке аутентификации"
        )


# Экспортируем зависимости для использования в эндпоинтах
# ВАЖНО: Убрали Depends() здесь, так как зависимости должны добавляться в эндпоинтах
# get_current_user_dep = Depends(get_current_user)
# require_telegram_auth_dep = Depends(require_telegram_auth)
# require_telegram_web_app_dep = Depends(require_telegram_web_app)

# Вместо этого экспортируем функции, которые можно использовать с Depends()
get_current_user_dep = get_current_user
require_telegram_auth_dep = require_telegram_auth
require_telegram_web_app_dep = require_telegram_web_app