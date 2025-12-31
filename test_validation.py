"""
Test script to validate Telegram init data validation and user creation
"""
import sys
sys.path.insert(0, '/workspace/codeProject/backend')

from app.core.telegram import validate_telegram_init_data, get_telegram_user_data
from urllib.parse import urlencode
import hashlib
import hmac
import time
import json

def generate_test_init_data():
    """Generate test Telegram init data with fake bot token"""
    # User data
    user_data = {
        "id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "language_code": "en",
        "is_premium": True
    }
    
    # Current timestamp
    auth_date = int(time.time())
    
    # Create init data dict - order doesn't matter here, it will be sorted during validation
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
    
    print(f"Data check string: {data_check_string}")
    
    # Create hash using our test token
    bot_token = "1234567890:ABCdefGhIjKlMnOpQrStUvWxYz123456789"
    secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    # Create the final init data string
    init_data_parts = [f"{key}={value}" for key, value in init_data_dict.items()]
    test_init_data = '&'.join(init_data_parts) + f"&hash={expected_hash}"
    
    print(f"Generated test init data: {test_init_data}")
    print(f"Auth date: {auth_date}")
    
    return test_init_data

def test_validation():
    """Test the validation with generated test data"""
    print("Testing Telegram init data validation...")
    
    # Generate test data
    test_data = generate_test_init_data()
    
    try:
        # Test validation
        result = validate_telegram_init_data(test_data)
        print(f"Validation result: {result}")
        
        # Test user data extraction
        user_data = get_telegram_user_data(test_data)
        print(f"Extracted user data: {user_data}")
        
        return True
    except Exception as e:
        print(f"Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_validation()