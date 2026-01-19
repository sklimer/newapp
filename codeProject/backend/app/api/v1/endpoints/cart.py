import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel

from app.api.deps import get_db
from app.models.users import User
from app.models.cart import CartItem
from app.models.menu import Product
from app.schemas.cart import CartItemResponse, CartItemCreate, CartItemUpdate

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)


class TelegramAuth(BaseModel):
    """Модель для передачи Telegram ID"""
    telegram_id: Optional[int] = None


# Dependency для получения пользователя по telegram_id
async def get_user_by_telegram_id(
        telegram_id: Optional[int] = Query(None, description="Telegram ID пользователя"),
        telegram_auth: Optional[TelegramAuth] = Body(None, description="Telegram ID в теле запроса")
) -> User:
    """
    Получает пользователя по telegram_id из query параметра или тела запроса
    """
    # Определяем telegram_id из разных источников
    final_telegram_id = None

    if telegram_id:
        final_telegram_id = telegram_id
    elif telegram_auth and telegram_auth.telegram_id:
        final_telegram_id = telegram_auth.telegram_id

    if not final_telegram_id:
        raise HTTPException(status_code=400, detail="Telegram ID не указан")

    return final_telegram_id


# Вспомогательная функция для получения пользователя из БД
async def get_user_from_db(telegram_id: int, db: AsyncSession) -> User:
    """Находит пользователя в БД по telegram_id"""
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Можно создать нового пользователя автоматически
        # или вернуть ошибку
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


@router.post("/add", response_model=CartItemResponse)
async def add_to_cart(
        cart_item: CartItemCreate,
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_db)
):
    """
    Добавляет товар в корзину по telegram_id
    Использование: /add?telegram_id=123456789
    """
    logger.info(f"Добавление в корзину для пользователя {telegram_id}: product_id={cart_item.product_id}, quantity={cart_item.quantity}")

    # Получаем пользователя
    user = await get_user_from_db(telegram_id, db)
    logger.info(f"Найден пользователь с ID {user.id} для telegram_id {telegram_id}")

    # Проверяем, существует ли продукт
    product_result = await db.execute(
        select(Product).where(Product.id == cart_item.product_id)
    )
    product = product_result.scalar_one_or_none()
    if not product:
        logger.error(f"Товар с ID {cart_item.product_id} не найден в базе данных")
        raise HTTPException(status_code=404, detail="Товар не найден")

    logger.info(f"Найден товар: {product.name}, цена: {product.price}")

    # Проверяем, есть ли уже такой товар в корзине у пользователя
    existing_item_result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == user.id,
            CartItem.product_id == cart_item.product_id
        )
    )
    existing_item = existing_item_result.scalar_one_or_none()

    if existing_item:
        old_quantity = existing_item.quantity
        existing_item.quantity += cart_item.quantity
        await db.commit()
        await db.refresh(existing_item)
        logger.info(f"Обновлено количество товара в корзине: {old_quantity} -> {existing_item.quantity}")
        return existing_item
    else:
        # Создаем новый элемент корзины
        db_cart_item = CartItem(
            user_id=user.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(db_cart_item)
        await db.commit()
        await db.refresh(db_cart_item)
        logger.info(f"Новый товар добавлен в корзину: ID {db_cart_item.id}, product_id {db_cart_item.product_id}, quantity {db_cart_item.quantity}")
        return db_cart_item


@router.get("/", response_model=List[CartItemResponse])
async def get_cart(
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_db)
):
    """
    Получает корзину пользователя по telegram_id
    Использование: /?telegram_id=123456789
    """
    logger.info(f'Получение корзины для пользователя {telegram_id}')

    # Получаем пользователя
    user = await get_user_from_db(telegram_id, db)
    logger.info(f"Найден пользователь с ID {user.id} для telegram_id {telegram_id}")

    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user.id)
    )
    cart_items = result.scalars().all()
    
    logger.info(f"Найдено {len(cart_items)} товаров в корзине пользователя {telegram_id}")

    # Добавляем информацию о продуктах и возвращаем объекты модели напрямую
    enriched_items = []
    for item in cart_items:
        logger.info(f"Обработка товара в корзине: ID {item.id}, product_id {item.product_id}, quantity {item.quantity}")
        
        # Получаем продукт
        product_result = await db.execute(
            select(Product).where(Product.id == item.product_id)
        )
        product = product_result.scalar_one_or_none()

        if not product:
            logger.warning(f"Продукт с ID {item.product_id} не найден для элемента корзины {item.id}")
            
        # Создаем словарь с данными элемента корзины, включая даты
        item_dict = {
            "id": item.id,
            "user_id": item.user_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "product": {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "image_url": product.image_url
            } if product else None
        }
        enriched_items.append(item_dict)

    logger.info(f"Возвращено {len(enriched_items)} элементов корзины для пользователя {telegram_id}")
    return enriched_items


@router.put("/update", response_model=CartItemResponse)
async def update_cart_item(
        cart_item_update: CartItemUpdate,
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_db)
):
    """
    Обновляет количество товара в корзине
    Использование: /update?telegram_id=123456789
    """
    logger.info(f"Обновление корзины для пользователя {telegram_id}: product_id={cart_item_update.product_id}, new_quantity={cart_item_update.quantity}")

    # Получаем пользователя
    user = await get_user_from_db(telegram_id, db)
    logger.info(f"Найден пользователь с ID {user.id} для telegram_id {telegram_id}")

    result = await db.execute(
        select(CartItem).where(
            CartItem.product_id == cart_item_update.product_id,
            CartItem.user_id == user.id
        )
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        logger.warning(f"Элемент корзины с product_id {cart_item_update.product_id} не найден для пользователя {user.id}")
        raise HTTPException(status_code=404, detail="Элемент корзины не найден")

    logger.info(f"Найден элемент корзины: ID {cart_item.id}, текущее количество: {cart_item.quantity}")

    if cart_item_update.quantity is not None:
        if cart_item_update.quantity <= 0:
            # Если количество <= 0, удаляем элемент
            logger.info(f"Удаление товара из корзины (количество <= 0)")
            await db.delete(cart_item)
            await db.commit()
            return {"detail": "Товар удален из корзины"}
        else:
            old_quantity = cart_item.quantity
            cart_item.quantity = cart_item_update.quantity
            logger.info(f"Обновление количества: {old_quantity} -> {cart_item.quantity}")

    await db.commit()
    await db.refresh(cart_item)
    logger.info(f"Корзина обновлена: ID {cart_item.id}, новое количество: {cart_item.quantity}")
    return cart_item


@router.delete("/remove")
async def remove_from_cart(
        product_id: int = Query(..., description="ID товара"),
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_db)
):
    """
    Удаляет товар из корзины
    Использование: /remove?telegram_id=123456789&product_id=1
    """
    logger.info(f"Удаление товара {product_id} из корзины пользователя {telegram_id}")

    # Получаем пользователя
    try:
        user = await get_user_from_db(telegram_id, db)
        logger.info(f"Найден пользователь с ID {user.id} для telegram_id {telegram_id}")
    except HTTPException:
        logger.error(f"Пользователь с telegram_id {telegram_id} не найден")
        raise

    # Проверяем, какие товары есть в корзине пользователя
    all_cart_items_result = await db.execute(
        select(CartItem).where(CartItem.user_id == user.id)
    )
    all_cart_items = all_cart_items_result.scalars().all()
    logger.info(f"Товары в корзине пользователя {telegram_id}: {[item.product_id for item in all_cart_items]}")

    result = await db.execute(
        select(CartItem).where(
            CartItem.product_id == product_id,
            CartItem.user_id == user.id
        )
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        logger.warning(f"Товар с product_id {product_id} не найден в корзине пользователя {user.id}")
        raise HTTPException(status_code=404, detail="Товар не найден в корзине")

    logger.info(f"Найден товар в корзине: ID {cart_item.id}, product_id {cart_item.product_id}, quantity {cart_item.quantity}")

    await db.delete(cart_item)
    await db.commit()
    logger.info(f"Товар {product_id} успешно удален из корзины пользователя {telegram_id}")
    return {"detail": "Товар успешно удален из корзины", "product_id": product_id}


@router.delete("/clear")
async def clear_cart(
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_db)
):
    """
    Очищает всю корзину пользователя
    Использование: /clear?telegram_id=123456789
    """
    logger.info(f"Очистка корзины для пользователя {telegram_id}")

    # Получаем пользователя
    user = await get_user_from_db(telegram_id, db)
    logger.info(f"Найден пользователь с ID {user.id} для telegram_id {telegram_id}")

    # Находим все элементы корзины пользователя
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user.id)
    )
    cart_items = result.scalars().all()

    logger.info(f"Найдено {len(cart_items)} элементов для удаления из корзины пользователя {telegram_id}")

    # Удаляем все элементы
    deleted_items_count = 0
    for item in cart_items:
        logger.info(f"Удаление элемента корзины: ID {item.id}, product_id {item.product_id}")
        await db.delete(item)
        deleted_items_count += 1

    await db.commit()

    logger.info(f"Корзина пользователя {telegram_id} очищена, удалено {deleted_items_count} элементов")
    
    return {
        "detail": "Корзина успешно очищена",
        "cleared_items": len(cart_items)
    }


# Альтернативная версия endpoints с передачей telegram_id в теле запроса
@router.post("/add-v2", response_model=CartItemResponse)
async def add_to_cart_v2(
        cart_item: CartItemCreate,
        telegram_auth: TelegramAuth = Body(...),
        db: AsyncSession = Depends(get_db)
):
    """
    Альтернативная версия добавления в корзину с передачей telegram_id в теле запроса
    """
    if not telegram_auth.telegram_id:
        raise HTTPException(status_code=400, detail="Telegram ID не указан")

    return await add_to_cart(cart_item, telegram_auth.telegram_id, db)


@router.get("/v2", response_model=List[CartItemResponse])
async def get_cart_v2(
        telegram_auth: TelegramAuth = Body(...),
        db: AsyncSession = Depends(get_db)
):
    """
    Альтернативная версия получения корзины с передачей telegram_id в теле запроса
    """
    if not telegram_auth.telegram_id:
        raise HTTPException(status_code=400, detail="Telegram ID не указан")

    return await get_cart(telegram_auth.telegram_id, db)


# Endpoint для получения количества товаров в корзине
@router.get("/count")
async def get_cart_count(
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_db)
):
    """
    Получает количество уникальных товаров в корзине
    """
    user = await get_user_from_db(telegram_id, db)

    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user.id)
    )
    cart_items = result.scalars().all()

    total_items = sum(item.quantity for item in cart_items)
    unique_items = len(cart_items)

    return {
        "telegram_id": telegram_id,
        "unique_items": unique_items,
        "total_items": total_items,
        "cart_items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity
            }
            for item in cart_items
        ]
    }


# Endpoint для массового обновления корзины
@router.put("/batch-update")
async def batch_update_cart(
        updates: List[CartItemUpdate],
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_db)
):
    """
    Массовое обновление корзины
    """
    user = await get_user_from_db(telegram_id, db)
    results = []

    for update in updates:
        result = await db.execute(
            select(CartItem).where(
                CartItem.product_id == update.product_id,
                CartItem.user_id == user.id
            )
        )
        cart_item = result.scalar_one_or_none()

        if cart_item:
            if update.quantity and update.quantity > 0:
                cart_item.quantity = update.quantity
                results.append({
                    "product_id": update.product_id,
                    "status": "updated",
                    "new_quantity": update.quantity
                })
            elif update.quantity == 0:
                await db.delete(cart_item)
                results.append({
                    "product_id": update.product_id,
                    "status": "removed"
                })
        else:
            # Если товара нет в корзине, но quantity > 0 - добавляем
            if update.quantity and update.quantity > 0:
                # Проверяем существование товара
                product_result = await db.execute(
                    select(Product).where(Product.id == update.product_id)
                )
                product = product_result.scalar_one_or_none()

                if product:
                    new_item = CartItem(
                        user_id=user.id,
                        product_id=update.product_id,
                        quantity=update.quantity
                    )
                    db.add(new_item)
                    results.append({
                        "product_id": update.product_id,
                        "status": "added",
                        "quantity": update.quantity
                    })

    await db.commit()

    return {
        "telegram_id": telegram_id,
        "updates": results
    }