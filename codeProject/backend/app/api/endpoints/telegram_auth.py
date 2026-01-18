import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import get_or_create_user_from_telegram
from app.models.users import User
from app.schemas.users import UserResponse

router = APIRouter()

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@router.get("/", response_model=UserResponse)
async def get_current_user_from_telegram(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user from Telegram Web App data, creating if doesn't exist
    """
    logging.info("get_current_user_from_telegram")
    user = await get_or_create_user_from_telegram(request, db)
    logger.info(f"get_current_user_from_telegram= {user}")
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="This application must be accessed through Telegram Web App with valid init data"
        )
    return UserResponse.from_orm(user)