import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import settings
from .telegram import validate_telegram_init_data, get_telegram_user_data, is_running_in_telegram_web_app

security = HTTPBearer()

logger = logging.getLogger(__name__)
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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

    def validate_telegram_request(request: Request):
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

    def check_telegram_environment(request: Request):
        if not is_running_in_telegram_web_app(request):
            raise HTTPException(status_code=400, detail="This endpoint is only accessible from Telegram Web App")
        return True

    return check_telegram_environment


def get_or_create_user_from_telegram_sync(
        telegram_user_data: Dict[str, Any],
        db: Session
):
    """
    Get or create user from Telegram data (synchronous version)

    Args:
        telegram_user_data: Dictionary with Telegram user data from validated initData
        db: Database session

    Returns:
        User object or None
    """
    try:
        # Validate required Telegram user data
        if not telegram_user_data or 'id' not in telegram_user_data:
            logger.error("Missing Telegram user data or user ID")
            return None

        telegram_id = str(telegram_user_data['id'])
        first_name = telegram_user_data.get('first_name', '')
        last_name = telegram_user_data.get('last_name')
        username = telegram_user_data.get('username')
        photo_url = telegram_user_data.get('photo_url')
        language_code = telegram_user_data.get('language_code')
        is_premium = telegram_user_data.get('is_premium', False)

        logger.info(f"Processing Telegram user: {telegram_id}, username: {username}")

        # Check if user already exists by telegram_id
        from app.models.users import User as UserModel
        from datetime import datetime

        db_user = db.query(UserModel).filter(UserModel.telegram_id == telegram_id).first()

        if db_user:
            # Update user data if changed
            update_fields = {
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'updated_at': datetime.utcnow()
            }

            updated = False
            for field, value in update_fields.items():
                if value is not None:
                    current_value = getattr(db_user, field)
                    if current_value != value:
                        setattr(db_user, field, value)
                        updated = True
                        logger.debug(f"Updated field {field}: {current_value} -> {value}")

            if updated:
                db.commit()
                db.refresh(db_user)
                logger.info(f"Updated existing user: {telegram_id}")
            else:
                logger.info(f"User exists, no changes needed: {telegram_id}")

            return db_user
        else:
            # Create new user
            user_create_data = {
                'telegram_id': telegram_id,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'photo_url': photo_url,
                'language_code': language_code,
                'is_premium': is_premium,
                'last_login': datetime.utcnow(),
                # Generate referral code based on Telegram ID
                'referral_code': f"REF{telegram_id[-6:].upper()}" if len(telegram_id) >= 6 else f"REF{telegram_id}"
            }

            # Remove None values
            user_create_data = {k: v for k, v in user_create_data.items() if v is not None}

            db_user = UserModel(**user_create_data)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            logger.info(f"Created new user: {telegram_id}, referral_code: {db_user.referral_code}")
            return db_user

    except Exception as e:
        logger.error(f"Unexpected error in get_or_create_user_from_telegram_sync: {str(e)}", exc_info=True)
        # Rollback any changes if there was an error
        try:
            db.rollback()
        except:
            pass
        return None