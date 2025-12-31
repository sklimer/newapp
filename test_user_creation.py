#!/usr/bin/env python3
"""
Тестирование автоматического создания пользователя при обращении к API
"""
import asyncio
import json
import sys
import os
from urllib.parse import urlencode
import hashlib
import hmac
import time

# Добавляем путь к backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'codeProject/backend'))

from fastapi.testclient import TestClient
from codeProject.backend.app.main import app

client = TestClient(app)

def create_telegram_init_data(user_data):
    """Создает поддельные данные инициализации Telegram для тестирования"""
    # Создаем строку данных пользователя
    user_data_str = json.dumps(user_data)
    
    # Формируем строку для подписи
    auth_date = str(int(time.time()))
    data_to_sign = f"auth_date={auth_date}\nquery_id=TEST_QUERY_ID\nuser={user_data_str}"
    
    # Создаем подпись (в тестах используем фиктивный токен)
    secret_key = hmac.new(
        b'WebAppData',
        '123456:TEST_BOT_TOKEN_FOR_TESTING'.encode(),
        hashlib.sha256
    ).digest()
    
    signature = hmac.new(
        secret_key,
        data_to_sign.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Формируем строку инициализации
    init_data = f"{data_to_sign}&hash={signature}"
    return init_data

async def test_user_creation():
    """Тестирует создание пользователя при обращении к профилю"""
    # Данные тестового пользователя Telegram
    user_data = {
        "id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "language_code": "en",
        "is_premium": True
    }
    
    # Создаем поддельные данные инициализации
    init_data = create_telegram_init_data(user_data)
    
    # Отправляем запрос к эндпоинту профиля с заголовком Telegram
    headers = {
        "x-telegram-web-app-init-data": init_data
    }
    
    response = client.get("/api/v1/profile/", headers=headers)
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"User created/retrieved successfully: {user_info}")
        print(f"User ID: {user_info.get('id')}")
        print(f"Telegram ID: {user_info.get('telegram_id')}")
        print(f"First name: {user_info.get('first_name')}")
        print(f"Last name: {user_info.get('last_name')}")
        print(f"Username: {user_info.get('username')}")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    asyncio.run(test_user_creation())