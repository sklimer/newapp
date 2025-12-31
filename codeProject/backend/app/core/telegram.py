import logging
import hashlib
import hmac
import urllib.parse
from typing import Dict, Any
from fastapi import HTTPException, Request
from .config import settings
import time
import json


def validate_telegram_init_data(init_data: str) -> bool:
    """
    Validates Telegram init data according to official documentation
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    """
    try:
        # Parse the init data
        parsed_params = dict(urllib.parse.parse_qsl(init_data))
        
        # Get the received hash
        received_hash = parsed_params.get('hash')
        if not received_hash:
            raise HTTPException(status_code=400, detail="Missing hash in init data")
        
        # Remove hash from params to form the data_check_string
        items_to_sign = []
        for key, value in sorted(parsed_params.items()):
            if key != 'hash':
                items_to_sign.append(f"{key}={value}")
        data_check_string = '\n'.join(items_to_sign)
        
        # Create secret key using HMAC-SHA256 with the string "WebAppData" and bot token
        secret_key = hmac.new(
            b'WebAppData',
            settings.TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # Calculate expected hash
        expected_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare hashes
        if not hmac.compare_digest(expected_hash, received_hash):
            raise HTTPException(status_code=400, detail="Invalid init data hash")
        
        # Check if the data is not expired (within 1 hour for safety)
        auth_date = parsed_params.get('auth_date')
        if auth_date:
            current_time = int(time.time())
            auth_time = int(auth_date)
            
            # Check if auth_date is older than 1 hour (3600 seconds)
            if current_time - auth_time > 3600:
                raise HTTPException(status_code=400, detail="Auth date is too old")
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error validating Telegram init data: {e}")
        raise HTTPException(status_code=400, detail="Invalid init data")


def get_telegram_user_data(init_data: str) -> Dict[str, Any]:
    """
    Extracts user data from Telegram init data after validation
    """
    try:
        parsed_params = dict(urllib.parse.parse_qsl(init_data))
        user_data_str = parsed_params.get('user')
        if not user_data_str:
            raise HTTPException(status_code=400, detail="No user data found")
        
        user_data = json.loads(user_data_str)
        return user_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not extract user data: {e}")


def is_running_in_telegram_web_app(request: Request) -> bool:
    """
    Checks if the request is coming from Telegram Web App
    """
    user_agent = request.headers.get("user-agent", "")
    telegram_web_app_header = request.headers.get("x-telegram-web-app-init-data")
    referer = request.headers.get("referer", "")
    
    # Check if it's from Telegram Web App environment
    is_telegram_env = (
        "Telegram" in user_agent or 
        "tgWebApp" in user_agent or 
        telegram_web_app_header is not None or
        "t.me" in referer or
        "web.telegram.org" in referer
    )
    
    return is_telegram_env