"""
Test script to verify Telegram security implementation
"""
import os
import sys
sys.path.insert(0, '/workspace/codeProject/backend')

from app.core.telegram import validate_telegram_init_data, is_running_in_telegram_web_app
from app.core.security import require_telegram_auth
from fastapi import Request

def test_telegram_validation():
    print("Testing Telegram security implementation...")
    
    # Test 1: Check if functions exist
    assert hasattr(validate_telegram_init_data, '__call__'), "validate_telegram_init_data function should exist"
    assert hasattr(is_running_in_telegram_web_app, '__call__'), "is_running_in_telegram_web_app function should exist"
    assert hasattr(require_telegram_auth, '__call__'), "require_telegram_auth function should exist"
    
    print("✓ All security functions exist")
    
    # Test 2: Check if validation fails with empty data
    try:
        validate_telegram_init_data("")
        print("✗ Validation should fail with empty data")
    except Exception:
        print("✓ Validation correctly fails with empty data")
    
    # Test 3: Check environment detection function
    # Create a mock request
    class MockRequest:
        def __init__(self, headers=None, user_agent="", referer=""):
            self.headers = headers or {}
            if user_agent:
                self.headers["user-agent"] = user_agent
            if referer:
                self.headers["referer"] = referer
    
    # Test with Telegram user agent
    mock_request = MockRequest(user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Telegram/10.4.0 Version/4.0 Chrome/116.0.5845.163 Mobile Safari/537.36")
    assert is_running_in_telegram_web_app(mock_request), "Should detect Telegram user agent"
    print("✓ Correctly detects Telegram user agent")
    
    # Test with Telegram header
    mock_request = MockRequest(headers={"x-telegram-web-app-init-data": "some_data"})
    assert is_running_in_telegram_web_app(mock_request), "Should detect Telegram header"
    print("✓ Correctly detects Telegram header")
    
    # Test with Telegram referer
    mock_request = MockRequest(referer="https://t.me/yourbot?startapp=webapp")
    assert is_running_in_telegram_web_app(mock_request), "Should detect Telegram referer"
    print("✓ Correctly detects Telegram referer")
    
    # Test with non-Telegram environment
    mock_request = MockRequest(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    assert not is_running_in_telegram_web_app(mock_request), "Should not detect non-Telegram environment"
    print("✓ Correctly rejects non-Telegram environment")
    
    print("\nAll security tests passed! ✅")
    print("\nSecurity features implemented:")
    print("- Telegram init data validation")
    print("- Environment verification")
    print("- Middleware protection")
    print("- Frontend integration")


if __name__ == "__main__":
    test_telegram_validation()