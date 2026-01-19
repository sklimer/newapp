from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_or_create_user_from_telegram
from app.models.users import User
from app.schemas.auth import TokenData


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Получить текущего пользователя по токену
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    from sqlalchemy.future import select
    result = await db.execute(select(User).filter(User.id == token_data.user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_from_telegram(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current user from Telegram Web App data, creating if doesn't exist
    """
    # Check if request is coming from Telegram Web App
    from app.core.telegram import is_running_in_telegram_web_app
    if not is_running_in_telegram_web_app(request):
        raise HTTPException(status_code=400, detail="Request must come from Telegram Web App")

    # Get init data from header or query parameter
    init_data = request.headers.get("x-telegram-web-app-init-data")
    if not init_data:
        # Try to get from form data or query parameters if not in header
        init_data = request.query_params.get("initData")
        if not init_data:
            raise HTTPException(status_code=400, detail="Missing Telegram init data")

    # Validate the init data
    from app.core.telegram import validate_telegram_init_data, get_telegram_user_data
    validate_telegram_init_data(init_data)

    # Get validated user data
    telegram_user_data = get_telegram_user_data(init_data)

    # Get or create user from Telegram data
    from app.core.security import get_or_create_user_from_telegram
    user = await get_or_create_user_from_telegram(telegram_user_data, db)
    if user is None:
        raise HTTPException(status_code=400, detail="Request must come from Telegram Web App with valid init data")
    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Проверить, является ли пользователь администратором
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user