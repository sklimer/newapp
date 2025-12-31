# API Documentation

## Profile Endpoints

### Get Profile
```
GET /api/v1/profile/
```

**Description:** Get current user profile information.

**Authentication:** Requires Telegram Web App environment with valid init data in headers.

**Headers:**
- `x-telegram-web-app-init-data`: Telegram init data

**Response:**
```json
{
  "id": 1,
  "telegram_id": "123456789",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "email": "john@example.com",
  "address_lat": 55.123456,
  "address_lon": 37.123456,
  "address_description": "Near the park",
  "bonus_balance": 0.0,
  "total_spent": 0.0,
  "order_count": 0,
  "is_active": true,
  "is_blocked": false,
  "referral_code": "REF123456",
  "referred_by": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Update Profile
```
PUT /api/v1/profile/
```

**Description:** Update current user profile information.

**Authentication:** Requires Telegram Web App environment with valid init data in headers.

**Headers:**
- `x-telegram-web-app-init-data`: Telegram init data

**Request Body:**
```json
{
  "username": "newusername",
  "first_name": "Jane",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "email": "jane@example.com",
  "address_lat": 55.123456,
  "address_lon": 37.123456,
  "address_description": "New address",
  "is_blocked": false
}
```

**Response:**
```json
{
  "id": 1,
  "telegram_id": "123456789",
  "username": "newusername",
  "first_name": "Jane",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "email": "jane@example.com",
  "address_lat": 55.123456,
  "address_lon": 37.123456,
  "address_description": "New address",
  "bonus_balance": 0.0,
  "total_spent": 0.0,
  "order_count": 0,
  "is_active": true,
  "is_blocked": false,
  "referral_code": "REF123456",
  "referred_by": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## Cart Endpoints

All cart endpoints now automatically check for user existence and create a new user if needed when the request comes from Telegram Web App.

### Add to Cart
```
POST /api/v1/cart/
```

**Description:** Add item to user's cart. Automatically creates user if not exists.

**Authentication:** Requires Telegram Web App environment with valid init data in headers.

**Headers:**
- `x-telegram-web-app-init-data`: Telegram init data

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 1,
  "quantity": 2,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## User Registration and Verification

### Telegram Authentication
```
POST /api/v1/users/telegram-auth
```

**Description:** Authenticate user via Telegram and create user if not exists.

**Authentication:** Requires Telegram Web App environment with valid init data in headers.

**Headers:**
- `x-telegram-web-app-init-data`: Telegram init data

**Response:**
```json
{
  "id": 1,
  "telegram_id": "123456789",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": null,
  "email": null,
  "address_lat": null,
  "address_lon": null,
  "address_description": null,
  "bonus_balance": 0.0,
  "total_spent": 0.0,
  "order_count": 0,
  "is_active": true,
  "is_blocked": false,
  "referral_code": "REF123456",
  "referred_by": null,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## Automatic User Verification

The system automatically verifies user existence and creates new users when:

1. A request comes from Telegram Web App environment
2. The user accesses any protected endpoint that requires Telegram authentication
3. The user interacts with cart functionality
4. The user accesses profile information

This is handled by the `get_current_user_from_telegram` dependency which ensures:
- User is validated through Telegram's authentication system
- User is created in the database if not exists
- User information is updated if changed
- All cart operations are linked to the authenticated user