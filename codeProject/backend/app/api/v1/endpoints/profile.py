import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.models.users import User
from app.schemas.users import UserResponse, UserUpdate, UserProfile
from app.api.deps import get_async_db

from app.api.v1.endpoints.util import get_user_from_db


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=UserProfile)
async def get_profile(
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_async_db)
):
    logger.info(f"Запрсо профиля для telegram_id {telegram_id}")
    """
    Get current user profile
    """
    # Получаем пользователя с загрузкой связанных данных если нужно
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    logger.info(f"Найден пользователь с ID {user.id} для telegram_id {telegram_id}")

    # Если нужно актуализировать статистику на основе заказов, раскомментируйте:
    # from app.models.order import Order
    # from sqlalchemy import func
    #
    # # Получаем актуальную статистику заказов
    # stats_stmt = select(
    #     func.count(Order.id).label("order_count"),
    #     func.coalesce(func.sum(Order.total_amount), 0).label("total_spent")
    # ).where(
    #     Order.user_id == user.id,
    #     Order.status.in_(["completed", "delivered"])  # Только завершенные заказы
    # )
    #
    # stats_result = await db.execute(stats_stmt)
    # stats = stats_result.fetchone()
    #
    # # Обновляем данные пользователя в памяти (без сохранения в БД)
    # user.order_count = stats.order_count or 0
    # user.total_spent = stats.total_spent or 0

    # Создаем профиль пользователя на основе модели User
    user_profile = UserProfile(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        bonus_balance=float(user.bonus_balance) if user.bonus_balance else 0.0,
        balance=float(user.balance) if user.balance else 0.0,
        total_spent=float(user.total_spent) if user.total_spent else 0.0,
        order_count=user.order_count or 0,
        is_active=user.is_active,
        is_blocked=user.is_blocked
    )

    logger.info(f"Создан профиль пользователя: {user.username or user.first_name}")
    return user_profile