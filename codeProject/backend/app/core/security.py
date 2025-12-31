import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .telegram import validate_telegram_init_data, get_telegram_user_data, is_running_in_telegram_web_app


security = HTTPBearer()


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user_id


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def require_telegram_auth():
    """
    Dependency to ensure requests come from Telegram and validate init data
    """
    async def validate_telegram_request(request: Request):
        # Check if request is coming from Telegram Web App
        if not is_running_in_telegram_web_app(request):
            raise HTTPException(status_code=400, detail="Request must come from Telegram Web App")
        
        # Get init data from header or query parameter
        init_data = request.headers.get("x-telegram-web-app-init-data")
        if not init_data:
            # Try to get from form data or query parameters if not in header
            init_data = request.query_params.get(" initData")
            if not init_data:
                raise HTTPException(status_code=400, detail="Missing Telegram init data")
        
        # Validate the init data
        validate_telegram_init_data(init_data)

        # Return validated user data
        return get_telegram_user_data(init_data)
    
    return validate_telegram_request


def require_telegram_web_app():
    """
    Dependency to ensure requests only come from Telegram Web App
    """
    async def check_telegram_environment(request: Request):
        if not is_running_in_telegram_web_app(request):
            raise HTTPException(status_code=400, detail="This endpoint is only accessible from Telegram Web App")
        return True
    
    return check_telegram_environment


async def get_or_create_user_from_telegram(request: Request, db: AsyncSession):
    """
    Get or create user from Telegram data
    """
    # Check if request is coming from Telegram Web App
    if not is_running_in_telegram_web_app(request):
        # If not in Telegram environment, return None without error
        return None

    # Get init data from header or query parameter
    init_data = request.headers.get("x-telegram-web-app-init-data")
    if not init_data:
        # Try to get from query parameters if not in header
        init_data = request.query_params.get("initData")
        if not init_data:
            # If no init data in headers or query params, return None without error
            return None
    
    try:
        # Validate the init data
        validate_telegram_init_data(init_data)

        # Get user data
        user_data = get_telegram_user_data(init_data)

        # Check if user already exists by telegram_id
        from app.models.users import User as UserModel
        from sqlalchemy.future import select

        result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == str(user_data['id']))
        )
        db_user = result.scalar_one_or_none()

        if db_user:
            # Update user data if changed
            update_fields = {
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'username': user_data.get('username'),
            }
            updated = False
            for field, value in update_fields.items():
                if value is not None and getattr(db_user, field) != value:
                    setattr(db_user, field, value)
                    updated = True

            if updated:
                await db.commit()
                await db.refresh(db_user)
            return db_user
        else:
            # Create new user
            user_create_data = {
                'telegram_id': str(user_data['id']),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'username': user_data.get('username'),
                'referral_code': f"REF{str(user_data['id'])[-6:].upper()}"  # Generate referral code
            }

            db_user = UserModel(**user_create_data)
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
    except HTTPException:
            # If there's a validation error (like invalid init data), return None
            # Don't raise the exception to avoid breaking the main page
            return None
    except Exception as e:
        # Log the error for debugging
        logging.error(f"Unexpected error in get_or_create_user_from_telegram: {e}")
        # For any other error, return None
        return None

