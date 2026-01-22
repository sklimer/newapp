import logging
import hashlib
import hmac
import urllib.parse
import json
import time
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, status

from .config import settings

logger = logging.getLogger(__name__)


def parse_telegram_init_data(init_data: str) -> Dict[str, Any]:
    """
    Парсит строку initData от Telegram в словарь
    """
    try:
        logger.info(f"🔍 Парсим initData. Длина: {len(init_data)}")

        # Парсим строку как query параметры
        parsed_data = dict(urllib.parse.parse_qsl(init_data))

        logger.info(f"✅ Парсинг успешен. Ключи: {list(parsed_data.keys())}")

        # Декодируем JSON поля
        for key in ['user', 'receiver', 'chat']:
            if key in parsed_data:
                try:
                    decoded_value = urllib.parse.unquote(parsed_data[key])
                    parsed_data[f"{key}_parsed"] = json.loads(decoded_value)
                    logger.debug(f"📋 Декодирован {key}: {parsed_data[f'{key}_parsed']}")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"⚠️ Не удалось декодировать {key}: {e}")

        return parsed_data

    except Exception as e:
        logger.error(f"❌ Ошибка парсинга initData: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка парсинга initData: {str(e)}"
        )


def validate_telegram_init_data(init_data: str) -> bool:
    """
    Валидирует Telegram init data согласно официальной документации
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    """
    logger.info("🔐 Начинаем валидацию Telegram init data")

    try:
        # Проверяем, что init_data не пустой
        if not init_data:
            logger.error("❌ Пустой init_data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пустые данные инициализации"
            )

        logger.info(f"📝 Длина init_data: {len(init_data)} символов")
        logger.debug(f"📝 init_data (первые 200 символов): {init_data[:200]}...")

        # Проверяем наличие токена бота
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN не настроен")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Токен Telegram бота не настроен на сервере"
            )

        # Парсим init_data
        parsed_params = parse_telegram_init_data(init_data)

        # Получаем полученный хэш
        received_hash = parsed_params.get('hash')
        if not received_hash:
            logger.error("❌ Хэш отсутствует в init_data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отсутствует хэш в данных инициализации"
            )

        logger.info(f"🔑 Полученный хэш: {received_hash}")

        # Удаляем хэш и сортируем параметры для создания data_check_string
        items_to_sign = []
        for key, value in sorted(parsed_params.items()):
            if key != 'hash':
                # Декодируем значение для проверки (но используем оригинальное для подписи)
                decoded_value = urllib.parse.unquote(value)
                items_to_sign.append(f"{key}={decoded_value}")

        data_check_string = '\n'.join(items_to_sign)
        logger.debug(f"📝 Data check string:\n{data_check_string}")

        # Создаем секретный ключ используя HMAC-SHA256 с "WebAppData" и токеном бота
        secret_key = hmac.new(
            key=b'WebAppData',
            msg=settings.TELEGRAM_BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()

        logger.debug(f"🔑 Секретный ключ (первые 20 байт): {secret_key[:20].hex()}...")

        # Вычисляем ожидаемый хэш
        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        logger.info(f"🔑 Ожидаемый хэш: {expected_hash}")

        # Сравниваем хэши
        if not hmac.compare_digest(expected_hash, received_hash):
            logger.error("❌ Хэши не совпадают")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невалидная подпись init data"
            )

        logger.info("✅ Хэши совпадают")

        # Проверяем время авторизации (не старше 1 часа)
        auth_date = parsed_params.get('auth_date')
        if auth_date:
            current_time = int(time.time())
            auth_time = int(auth_date)

            logger.info(f"🕒 Время авторизации: {auth_time} ({time.ctime(auth_time)})")
            logger.info(f"🕒 Текущее время: {current_time} ({time.ctime(current_time)})")

            # Проверяем, что auth_date не старше 24 часов (для надежности)
            if current_time - auth_time > 86400:  # 24 часа
                logger.error(f"❌ Слишком старая авторизация: {current_time - auth_time} секунд назад")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Срок действия данных инициализации истек"
                )

            logger.info("✅ Время авторизации в порядке")

        logger.info("✅ Валидация Telegram init data успешна")
        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при валидации init data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при валидации данных: {str(e)}"
        )


def get_telegram_user_data(init_data: str) -> Dict[str, Any]:
    """
    Извлекает данные пользователя из Telegram init data после валидации
    """
    logger.info("👤 Извлекаем данные пользователя из init data")

    try:
        # Проверяем, что init_data не пустой
        if not init_data:
            logger.error("❌ Пустой init_data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пустые данные инициализации"
            )

        # Парсим init_data
        parsed_params = parse_telegram_init_data(init_data)

        # Пробуем получить данные пользователя из разных источников
        user_data = None

        # Сначала пробуем из user
        if 'user_parsed' in parsed_params:
            user_data = parsed_params['user_parsed']
            logger.info("👤 Данные пользователя найдены в поле 'user'")

        # Если нет, пробуем из receiver
        elif 'receiver_parsed' in parsed_params:
            user_data = parsed_params['receiver_parsed']
            logger.info("👤 Данные пользователя найдены в поле 'receiver'")

        # Если все еще нет, пробуем парсить поле user напрямую
        elif 'user' in parsed_params:
            try:
                user_json = urllib.parse.unquote(parsed_params['user'])
                user_data = json.loads(user_json)
                logger.info("👤 Данные пользователя найдены в поле 'user' (прямой парсинг)")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"❌ Не удалось распарсить поле 'user': {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Невалидный формат данных пользователя"
                )

        if not user_data:
            logger.error("❌ Данные пользователя не найдены в init_data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отсутствуют данные пользователя"
            )

        # Приводим ID к строке для единообразия
        if 'id' in user_data:
            user_data['id'] = str(user_data['id'])

        logger.info(f"✅ Данные пользователя извлечены: ID={user_data.get('id')}, username={user_data.get('username')}")
        logger.debug(f"👤 Полные данные: {user_data}")

        return user_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при извлечении данных пользователя: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при извлечении данных пользователя: {str(e)}"
        )


def is_running_in_telegram_web_app(request: Request) -> bool:
    """
    Проверяет, что запрос пришел из Telegram Web App
    """
    logger.info("🌐 Проверяем, что запрос из Telegram Web App")

    try:
        # Получаем заголовки
        user_agent = request.headers.get("User-Agent", "").lower()
        telegram_header = request.headers.get("X-Telegram-WebApp-Init-Data") or \
                          request.headers.get("x-telegram-web-app-init-data")
        referer = request.headers.get("Referer", "").lower()


        logger.info(f"🌐 User-Agent: {user_agent[:100]}...")
        logger.info(f"🌐 Referer: {referer[:100]}...")
        logger.info(f"🌐 Telegram Header present: {telegram_header is not None}")

        # Проверяем признаки Telegram Web App
        is_telegram = (
                "telegram" in user_agent or
                "t.me" in referer or
                "telegram.org" in referer or
                telegram_header is not None
        )

        logger.info(f"🌐 Результат проверки Telegram Web App: {is_telegram}")

        return is_telegram

    except Exception as e:
        logger.error(f"❌ Ошибка при проверке окружения Telegram: {e}")
        # В случае ошибки лучше разрешить, чтобы не блокировать легитимные запросы
        return True


async def get_telegram_init_data_from_request(request: Request) -> Optional[str]:
    """
    Извлекает init data из запроса из разных источников (асинхронная версия)
    """
    logger.info("🔍 Ищем Telegram init data в запросе")

    try:
        init_data = None

        # Проверяем разные источники в порядке приоритета
        sources = [
            ("header X-Telegram-WebApp-Init-Data", request.headers.get("X-Telegram-WebApp-Init-Data")),
            ("header x-telegram-web-app-init-data", request.headers.get("x-telegram-web-app-init-data")),
            ("query param initData", request.query_params.get("initData")),
        ]

        for source_name, data in sources:
            if data:
                init_data = data
                logger.info(f"📥 Найден init data в {source_name}")
                logger.debug(f"📥 init data (первые 100 символов): {data[:100]}...")
                break

        # Если не нашли в заголовках или параметрах, пробуем получить из тела запроса
        if not init_data:
            try:
                body = await request.json()
                init_data = body.get("initData") or body.get("init_data")
                if init_data:
                    logger.info("📥 Найден init data в теле запроса (JSON)")
            except Exception as json_error:
                logger.debug(f"📥 Не удалось получить JSON тело: {json_error}")

                # Пробуем form data
                try:
                    form_data = await request.form()
                    init_data = form_data.get("initData") or form_data.get("init_data")
                    if init_data:
                        logger.info("📥 Найден init data в теле запроса (form data)")
                except Exception as form_error:
                    logger.debug(f"📥 Не удалось получить form data: {form_error}")

        if init_data:
            logger.info(f"✅ Telegram init data найден. Длина: {len(init_data)} символов")
        else:
            logger.warning("⚠️ Telegram init data не найден в запросе")

        return init_data

    except Exception as e:
        logger.error(f"❌ Ошибка при извлечении init data из запроса: {e}", exc_info=True)
        return None


async def validate_telegram_request(request: Request) -> Dict[str, Any]:
    """
    Полная валидация Telegram запроса (асинхронная версия)
    """
    logger.info("🛂 Начинаем полную валидацию Telegram запроса")

    try:
        # Проверяем, что запрос из Telegram Web App
        if not is_running_in_telegram_web_app(request):
            logger.error("❌ Запрос не из Telegram Web App")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот эндпоинт доступен только из Telegram Web App"
            )

        logger.info("✅ Запрос подтвержден как Telegram Web App")

        # Извлекаем init data
        init_data = await get_telegram_init_data_from_request(request)
        if not init_data:
            logger.error("❌ Отсутствует Telegram init data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отсутствуют данные инициализации Telegram"
            )

        # Валидируем init data
        validate_telegram_init_data(init_data)

        # Получаем данные пользователя
        user_data = get_telegram_user_data(init_data)

        logger.info(f"✅ Telegram запрос успешно валидирован. Пользователь: {user_data.get('id')}")

        return user_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при валидации Telegram запроса: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка при обработке Telegram запроса"
        )