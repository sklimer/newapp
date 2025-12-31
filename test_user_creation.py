"""
Test script to simulate user creation from Telegram Web App
"""
import asyncio
import sys
sys.path.insert(0, '/workspace/codeProject/backend')

from fastapi import Request
from unittest.mock import AsyncMock, MagicMock
from app.core.security import get_or_create_user_from_telegram
from app.core.database import get_db, async_engine, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User as UserModel
from app.core.telegram import validate_telegram_init_data, get_telegram_user_data
import json
import time
import hmac
import hashlib


def create_mock_request(init_data=None, user_agent="", referer=""):
    """Create a mock request with specific headers and query params"""
    request = MagicMock()
    request.headers = {}
    request.query_params = {}
    
    if init_data:
        request.headers["x-telegram-web-app-init-data"] = init_data
        # Also add to query params to test both methods
        request.query_params["initData"] = init_data
        request.query_params[" initData"] = init_data  # With space
    
    if user_agent:
        request.headers["user-agent"] = user_agent
    
    if referer:
        request.headers["referer"] = referer
    
    return request


async def test_user_creation():
    """Test the user creation process"""
    print("Testing user creation from Telegram init data...")
    
    # Create test init data
    user_data = {
        "id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "language_code": "en",
        "is_premium": True
    }
    
    auth_date = int(time.time())
    init_data_dict = {
        "user": json.dumps(user_data, separators=(',', ':')),
        "auth_date": str(auth_date),
        "chat_instance": "-123456789",
        "chat_type": "private"
    }
    
    # Create data check string by sorting parameters by key (as per Telegram documentation)
    data_check_string = '\n'.join([
        f"{key}={init_data_dict[key]}" 
        for key in sorted(init_data_dict.keys())
    ])
    
    # Create hash using test token
    bot_token = "1234567890:ABCdefGhIjKlMnOpQrStUvWxYz123456789"
    secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    # Create the final init data string
    init_data_parts = [f"{key}={value}" for key, value in init_data_dict.items()]
    test_init_data = '&'.join(init_data_parts) + f"&hash={expected_hash}"
    
    print(f"Generated test init data: {test_init_data[:100]}...")
    
    # Validate the data
    try:
        validate_telegram_init_data(test_init_data)
        print("✓ Init data validation successful")
        
        extracted_user_data = get_telegram_user_data(test_init_data)
        print(f"✓ Extracted user data: {extracted_user_data}")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False
    
    # Create mock request
    request = create_mock_request(
        init_data=test_init_data,
        user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Telegram/10.4.0 Version/4.0 Chrome/116.0.5845.163 Mobile Safari/537.36"
    )
    
    # Get database session
    async with AsyncSessionLocal() as db:
        # Try to get or create user
        user = await get_or_create_user_from_telegram(request, db)
        
        if user:
            print(f"✓ User created/retrieved successfully with ID: {user.id}, Telegram ID: {user.telegram_id}")
            print(f"  - First name: {user.first_name}")
            print(f"  - Last name: {user.last_name}")
            print(f"  - Username: {user.username}")
            print(f"  - Referral code: {user.referral_code}")
            return True
        else:
            print("✗ User was not created/retrieved")
            return False


if __name__ == "__main__":
    result = asyncio.run(test_user_creation())
    if result:
        print("\n✓ User creation test passed!")
    else:
        print("\n✗ User creation test failed!")