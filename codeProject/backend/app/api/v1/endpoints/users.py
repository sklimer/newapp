from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from datetime import datetime

from app.core.database import get_async_db
from app.core.security import get_current_user, require_telegram_auth, require_telegram_web_app
from app.schemas.users import User, UserCreate, UserUpdate
from app.models.users import User as UserModel
from app.schemas.orders import OrderSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User])
async def get_users(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
        limit: int = Query(100, ge=1, le=100, description="Лимит записей")
):
    """
    Получить список пользователей (только для админов)
    """
    try:
        # В реальном приложении здесь должна быть проверка прав админа
        result = await db.execute(
            select(UserModel)
            .where(UserModel.is_active == True)
            .order_by(UserModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        users = result.scalars().all()

        return [User.from_orm(user) for user in users]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении пользователей: {str(e)}"
        )


@router.get("/me", response_model=User)
async def get_current_user_profile(
        current_user_id: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    """
    Получить профиль текущего пользователя
    """
    try:
        result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        return User.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении профиля: {str(e)}"
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
        user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Получить пользователя по ID (только свой профиль)
    """
    try:
        # Находим текущего пользователя
        current_user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        current_user = current_user_result.scalar_one_or_none()

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Пользователь может получать только свой профиль
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )

        result = await db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        return User.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении пользователя: {str(e)}"
        )


@router.post("/", response_model=User)
async def create_user(
        user: UserCreate,
        db: AsyncSession = Depends(get_async_db)
):
    """
    Создать нового пользователя (для админов)
    """
    try:
        # Проверяем, существует ли пользователь с таким telegram_id
        result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == user.telegram_id)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Если пользователь уже существует, возвращаем его
            return User.from_orm(existing_user)

        # Проверяем, существует ли пользователь с таким email
        if user.email:
            result = await db.execute(
                select(UserModel).where(UserModel.email == user.email)
            )
            existing_email_user = result.scalar_one_or_none()

            if existing_email_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже существует"
                )

        # Генерируем реферальный код, если не указан
        if not user.referral_code:
            import secrets
            user.referral_code = f"REF{secrets.token_urlsafe(8).upper()[:8]}"

        # Проверяем, существует ли реферальный код в базе
        if user.referral_code:
            result = await db.execute(
                select(UserModel).where(UserModel.referral_code == user.referral_code)
            )
            existing_referral = result.scalar_one_or_none()

            if existing_referral:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Реферальный код уже используется"
                )

        # Создаем пользователя
        user_data = user.dict()
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()

        db_user = UserModel(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return User.from_orm(db_user)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании пользователя: {str(e)}"
        )


@router.put("/{user_id}", response_model=User)
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Обновить пользователя (только свой профиль)
    """
    try:
        # Находим текущего пользователя
        current_user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        current_user = current_user_result.scalar_one_or_none()

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Пользователь может обновлять только свой профиль
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )

        # Находим пользователя
        result = await db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Проверяем email на уникальность
        if user_update.email and user_update.email != db_user.email:
            result = await db.execute(
                select(UserModel).where(UserModel.email == user_update.email)
            )
            existing_email_user = result.scalar_one_or_none()

            if existing_email_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже существует"
                )

        # Обновляем данные
        update_data = user_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        await db.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**update_data)
        )

        await db.commit()

        # Получаем обновленного пользователя
        result = await db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        updated_user = result.scalar_one()

        return User.from_orm(updated_user)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении пользователя: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Удалить пользователя (мягкое удаление)
    """
    try:
        # Находим текущего пользователя
        current_user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        current_user = current_user_result.scalar_one_or_none()

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Пользователь может удалять только свой профиль
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )

        # Находим пользователя
        result = await db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Мягкое удаление
        await db.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                is_active=False,
                updated_at=datetime.utcnow()
            )
        )

        await db.commit()

        return {"message": "Пользователь успешно удален"}

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении пользователя: {str(e)}"
        )


@router.post("/telegram-auth", response_model=User)
async def telegram_auth(
        request: Request,
        db: AsyncSession = Depends(get_async_db),
        user_data: dict = Depends(require_telegram_auth)
):
    """
    Аутентификация пользователя через Telegram
    """
    try:
        telegram_id = str(user_data.get('id'))

        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отсутствует ID пользователя Telegram"
            )

        # Проверяем, существует ли пользователь
        result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Обновляем данные пользователя, если они изменились
            update_fields = {}

            if user_data.get('first_name') != user.first_name:
                update_fields['first_name'] = user_data.get('first_name')

            if user_data.get('last_name') != user.last_name:
                update_fields['last_name'] = user_data.get('last_name')

            if user_data.get('username') != user.username:
                update_fields['username'] = user_data.get('username')

            if user_data.get('photo_url') and user_data.get('photo_url') != user.photo_url:
                update_fields['photo_url'] = user_data.get('photo_url')

            if user_data.get('language_code') and user_data.get('language_code') != user.language_code:
                update_fields['language_code'] = user_data.get('language_code')

            if update_fields:
                update_fields['updated_at'] = datetime.utcnow()
                update_fields['last_login'] = datetime.utcnow()

                await db.execute(
                    update(UserModel)
                    .where(UserModel.id == user.id)
                    .values(**update_fields)
                )
            else:
                # Обновляем только время последнего входа
                await db.execute(
                    update(UserModel)
                    .where(UserModel.id == user.id)
                    .values(last_login=datetime.utcnow())
                )

            await db.commit()

            # Получаем обновленного пользователя
            result = await db.execute(
                select(UserModel).where(UserModel.id == user.id)
            )
            user = result.scalar_one()

            return User.from_orm(user)
        else:
            # Создаем нового пользователя
            import secrets

            # Генерируем реферальный код
            referral_code = f"REF{secrets.token_urlsafe(8).upper()[:8]}"

            # Проверяем уникальность реферального кода
            while True:
                result = await db.execute(
                    select(UserModel).where(UserModel.referral_code == referral_code)
                )
                existing = result.scalar_one_or_none()

                if not existing:
                    break
                referral_code = f"REF{secrets.token_urlsafe(8).upper()[:8]}"

            user_create_data = {
                'telegram_id': telegram_id,
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name'),
                'username': user_data.get('username'),
                'photo_url': user_data.get('photo_url'),
                'language_code': user_data.get('language_code'),
                'referral_code': referral_code,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'last_login': datetime.utcnow()
            }

            db_user = UserModel(**user_create_data)
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)

            return User.from_orm(db_user)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при аутентификации через Telegram: {str(e)}"
        )


@router.get("/{user_id}/orders", response_model=List[OrderSchema])
async def get_user_orders(
        user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user),
        skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
        limit: int = Query(100, ge=1, le=100, description="Лимит записей")
):
    """
    Получить заказы пользователя (только свои заказы)
    """
    try:
        # Находим текущего пользователя
        current_user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        current_user = current_user_result.scalar_one_or_none()

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Пользователь может получать только свои заказы
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )

        from app.models.orders import Order as OrderModel

        result = await db.execute(
            select(OrderModel)
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        orders = result.scalars().all()

        return [OrderSchema.from_orm(order) for order in orders]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении заказов: {str(e)}"
        )


@router.post("/{user_id}/add-bonus")
async def add_bonus_to_user(
        user_id: int,
        amount: float = Query(..., ge=0, description="Количество бонусов для добавления"),
        reason: str = Query(..., description="Причина начисления бонусов"),
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Добавить бонусы пользователю (только для админов)
    """
    try:
        # В реальном приложении здесь должна быть проверка прав админа
        # Пока что разрешаем только самому пользователю добавлять бонусы (для теста)

        # Находим текущего пользователя
        current_user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        current_user = current_user_result.scalar_one_or_none()

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Пользователь может добавлять бонусы только себе
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )

        # Находим пользователя
        result = await db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Добавляем бонусы
        await db.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                bonus_balance=UserModel.bonus_balance + amount,
                updated_at=datetime.utcnow()
            )
        )

        await db.commit()

        return {
            "message": f"Бонусы успешно добавлены",
            "user_id": user_id,
            "amount_added": amount,
            "reason": reason,
            "new_balance": user.bonus_balance + amount
        }

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении бонусов: {str(e)}"
        )


@router.get("/referral/{referral_code}", response_model=User)
async def get_user_by_referral_code(
        referral_code: str,
        db: AsyncSession = Depends(get_async_db)
):
    """
    Получить пользователя по реферальному коду
    """
    try:
        result = await db.execute(
            select(UserModel).where(
                UserModel.referral_code == referral_code,
                UserModel.is_active == True
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь с таким реферальным кодом не найден"
            )

        return User.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при поиске пользователя по реферальному коду: {str(e)}"
        )