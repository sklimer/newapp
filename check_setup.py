#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации приложения
"""

import sys
import os
sys.path.insert(0, '/workspace/codeProject/backend')

def check_database_connection():
    """Проверка подключения к базе данных"""
    print("🔍 Проверка конфигурации базы данных...")
    
    try:
        from app.core.config import settings
        print(f"✅ DATABASE_URL: {'*' * 20}{settings.DATABASE_URL[-10:] if settings.DATABASE_URL else 'NOT SET'}")
        print(f"✅ ASYNC_DATABASE_URL: {'*' * 20}{settings.ASYNC_DATABASE_URL[-10:] if settings.ASYNC_DATABASE_URL else 'NOT SET'}")
        
        # Проверяем подключение
        from sqlalchemy import text
        from app.core.database import sync_engine
        
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Синхронное подключение к базе данных работает")
        
        # Проверяем асинхронное подключение
        import asyncio
        from app.core.database import async_engine
        
        async def test_async_conn():
            async with async_engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                return True
        
        asyncio.run(test_async_conn())
        print("✅ Асинхронное подключение к базе данных работает")
        
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False
    
    return True

def check_api_routes():
    """Проверка маршрутов API"""
    print("\n🔍 Проверка маршрутов API...")
    
    try:
        from app.main import app
        print(f"✅ Приложение FastAPI создано: {app.title}")
        
        # Проверяем наличие основных маршрутов
        routes = [route.path for route in app.routes]
        if '/health' in routes:
            print("✅ Маршрут /health доступен")
        else:
            print("❌ Маршрут /health недоступен")
            
        if '/api/versions' in routes:
            print("✅ Маршрут /api/versions доступен")
        else:
            print("❌ Маршрут /api/versions недоступен")
            
        # Проверяем API версии
        if '/api/v1/menu/categories' in routes:
            print("✅ Маршрут /api/v1/menu/categories доступен")
        else:
            print("❌ Маршрут /api/v1/menu/categories недоступен")
            
        if '/api/v1/cart/' in routes:
            print("✅ Маршрут /api/v1/cart/ доступен")
        else:
            print("❌ Маршрут /api/v1/cart/ недоступен")
            
    except Exception as e:
        print(f"❌ Ошибка проверки маршрутов API: {e}")
        return False
    
    return True

def check_cors_configuration():
    """Проверка конфигурации CORS"""
    print("\n🔍 Проверка конфигурации CORS...")
    
    try:
        from app.main import app
        
        # Найти CORS middleware
        cors_found = False
        for middleware in app.user_middleware:
            if hasattr(middleware.cls, '__name__') and 'CORSMiddleware' in middleware.cls.__name__:
                cors_found = True
                break
        
        if cors_found:
            print("✅ CORS middleware настроен")
        else:
            print("❌ CORS middleware не найден")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки CORS: {e}")
        return False
    
    return True

def main():
    print("🚀 Запуск проверки конфигурации приложения...")
    print("="*50)
    
    checks = [
        check_database_connection(),
        check_api_routes(),
        check_cors_configuration()
    ]
    
    print("\n" + "="*50)
    if all(checks):
        print("✅ Все проверки пройдены успешно!")
        print("\n💡 Приложение готово к запуску")
        return True
    else:
        print("❌ Некоторые проверки не пройдены")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)