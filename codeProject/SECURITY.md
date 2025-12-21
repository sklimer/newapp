# Security Implementation for Telegram Mini App

## Overview

This document describes the security measures implemented for the Telegram Mini App to ensure that:

1. All requests are validated using Telegram's official authentication protocol
2. The application only functions within the Telegram Web App environment
3. Sensitive data and endpoints are protected

## Security Features

### 1. Telegram Init Data Validation

The application implements proper validation of Telegram init data according to the [official documentation](https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app).

#### Backend Implementation (`/backend/app/core/telegram.py`)

- **`validate_telegram_init_data(init_data)`**: Validates the hash signature of the init data
- **`get_telegram_user_data(init_data)`**: Extracts user information after validation
- **`is_running_in_telegram_web_app(request)`**: Checks if the request originates from Telegram

#### Validation Process

1. Parse the init data query string
2. Extract the `hash` parameter
3. Create a data check string from all other parameters sorted alphabetically
4. Generate the expected hash using HMAC-SHA256 with:
   - Secret key: `HMAC-SHA256("WebAppData", bot_token)`
   - Data: the data check string
5. Compare the received hash with the expected hash using secure comparison
6. Verify that the `auth_date` is not older than 1 hour

### 2. Telegram Web App Environment Check

The application verifies that requests are coming from a Telegram Web App environment by checking:

- `User-Agent` header for "Telegram" or "tgWebApp"
- Presence of `x-telegram-web-app-init-data` header
- `Referer` header containing "t.me" or "web.telegram.org"

### 3. Middleware Protection

A middleware (`TelegramWebAppMiddleware`) is implemented to restrict access to sensitive endpoints:

- `/api/v1/users/`
- `/api/v1/orders/`
- `/api/v1/cart/`
- `/api/v1/profile/`
- `/api/v1/payments/`

These endpoints will return a 400 error if accessed from outside the Telegram Web App environment.

### 4. Frontend Integration

The frontend automatically includes the Telegram init data in all API requests by:

1. Loading the Telegram Web App script in `index.html`
2. Adding the init data to the `x-telegram-web-app-init-data` header in the API interceptor
3. Handling Telegram-specific authentication errors

## API Endpoints with Telegram Authentication

### User Authentication

The `/api/v1/users/telegram-auth` endpoint now uses the new security functions:

- Requires valid Telegram init data
- Creates or updates user based on Telegram user information
- Returns user data with proper validation

## Configuration

### CORS Settings

The CORS settings in `config.py` have been restricted to only allow Telegram-related domains:

```python
ALLOWED_ORIGINS: list = [
    "https://web.telegram.org",
    "https://t.me",
    "https://www.t.me",
    "https://telegram.org"
]
```

## Security Best Practices Implemented

1. **Input Validation**: All Telegram init data is validated before processing
2. **Secure Hash Comparison**: Uses `hmac.compare_digest()` for timing-safe hash comparison
3. **Time-based Validation**: Checks that `auth_date` is not older than 1 hour
4. **Environment Verification**: Ensures requests come from Telegram environment
5. **Header-based Authentication**: Uses custom headers to pass init data
6. **Proper Error Handling**: Returns appropriate error messages without exposing sensitive information

## Testing

To test the security implementation:

1. Access the application from within a Telegram Web App - should work normally
2. Access restricted endpoints directly from browser - should return 400 error
3. Send invalid init data - should return 400 error
4. Send expired init data - should return 400 error

## Additional Recommendations

1. Ensure the `TELEGRAM_BOT_TOKEN` environment variable is properly set
2. Regularly rotate bot tokens if possible
3. Monitor access logs for suspicious activity
4. Consider implementing rate limiting
5. Use HTTPS in production