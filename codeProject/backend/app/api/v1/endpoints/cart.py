import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.api.deps import get_db, get_async_db
from app.models.users import User
from app.models.cart import CartItem
from app.models.menu import Product
from app.schemas.cart import CartItemResponse, CartItemCreate, CartItemUpdate, CartItemBatchUpdate


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
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


@router.post("/add", response_model=CartItemResponse)
async def add_to_cart(
        cart_item: CartItemCreate,
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_async_db)
):
    """
    Добавляет товар в корзину по telegram_id
    Использование: /add?telegram_id=123456789
    """
    logger.info(
        f"Добавление в корзину для пользователя {telegram_id}: product_id={cart_item.product_id}, quantity={cart_item.quantity}")

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
        logger.info(
            f"Новый товар добавлен в корзину: ID {db_cart_item.id}, product_id {db_cart_item.product_id}, quantity {db_cart_item.quantity}")
        return db_cart_item


@router.get("/", response_model=List[CartItemResponse])
async def get_cart(
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_async_db)
):
    """
    Получает корзину пользователя по telegram_id
    Использование: /?telegram_id=123456789
    """
    logger.info(f'Получение корзины для пользователя {telegram_id}')

    # Получаем пользователя
    user = await get_user_from_db(telegram_id, db)
    logger.info(f"Найден пользователь с ID {user.id} для telegram_id {telegram_id}")

    # Используем selectinload для жадной загрузки связанных данных
    stmt = select(CartItem).options(
        selectinload(CartItem.product)  # Жадная загрузка продукта
    ).where(
        CartItem.user_id == user.id
    )

    result = await db.execute(stmt)
    cart_items = result.scalars().all()

    logger.info(f"Найдено {len(cart_items)} товаров в корзине пользователя {telegram_id}")

    # Проверяем загрузку продуктов (теперь это безопасно)
    if cart_items:
        first_item = cart_items[0]
        if first_item.product:
            logger.info(f"Первый товар в корзине: {first_item.product.name}, цена: {first_item.product.price}")
        else:
            logger.warning(f"Продукт для первого элемента корзины не загружен")

    # Удаляем элементы корзины, для которых нет соответствующих продуктов
    items_to_delete = []
    for item in cart_items:
        if not item.product:
            logger.warning(f"Продукт с ID {item.product_id} не найден для элемента корзины {item.id}")
            items_to_delete.append(item)

    # Удаляем элементы без продуктов
    if items_to_delete:
        for item in items_to_delete:
            await db.delete(item)
        await db.commit()
        logger.info(f"Удалено {len(items_to_delete)} элементов корзины без соответствующих продуктов")
        # Обновляем список, удаляя удаленные элементы
        cart_items = [item for item in cart_items if item not in items_to_delete]

    # Возвращаем объекты модели напрямую (теперь с загруженными продуктами)
    logger.info(f"Возвращено {len(cart_items)} элементов корзины для пользователя {telegram_id}")
    logger.info(f"Возвращено {cart_items[0].product.name}")
    # Затем сериализуем через Pydantic
    cart_items_response = [CartItemResponse.from_orm(item) for item in cart_items]
    logger.info(f"Первый элемент после сериализации: {cart_items_response[0].dict()}")

    item = cart_items[0]
    cart_item_response = CartItemResponse(
        id=item.id,
        user_id=item.user_id,
        product_id=item.product_id,
        quantity=item.quantity,
        created_at=item.created_at,
        updated_at=item.updated_at,
        product=ProductResponse.from_orm(item.product) if item.product else None
    )
    logger.info(f"Manually created: {cart_item_response.dict()}")
    cart_items_response[0] = cart_item_response
    return cart_items_response


@router.put("/update", response_model=CartItemResponse)
async def update_cart_item(
        cart_item_update: CartItemUpdate,
        product_id: int = Query(..., description="ID товара"),
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_async_db)
):
    """
    Обновляет количество товара в корзине
    Использование: /update?telegram_id=123456789&product_id=1
    """
    logger.info(
        f"Обновление корзины для пользователя {telegram_id}: product_id={product_id}, new_quantity={cart_item_update.quantity}")

    # Получаем пользователя
    user = await get_user_from_db(telegram_id, db)
    logger.info(f"Найден пользователь с ID {user.id} для telegram_id {telegram_id}")

    # Используем selectinload для загрузки связанного продукта
    stmt = select(CartItem).options(
        selectinload(CartItem.product)
    ).where(
        CartItem.product_id == product_id,
        CartItem.user_id == user.id
    )

    result = await db.execute(stmt)
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        logger.warning(f"Элемент корзины с product_id {product_id} не найден для пользователя {user.id}")
        raise HTTPException(status_code=404, detail="Элемент корзины не найден")

    # Проверяем, существует ли продукт
    if not cart_item.product:
        logger.warning(f"Продукт с ID {product_id} не найден в базе данных, элемент корзины будет удален")
        await db.delete(cart_item)
        await db.commit()
        raise HTTPException(status_code=404, detail="Продукт больше не доступен")

    logger.info(f"Найден элемент корзины: ID {cart_item.id}, текущее количество: {cart_item.quantity}")

    if cart_item_update.quantity is not None:
        if cart_item_update.quantity <= 0:
            # Если количество <= 0, удаляем элемент
            logger.info(f"Удаление товара из корзины (количество <= 0)")
            await db.delete(cart_item)
            await db.commit()
            raise HTTPException(status_code=200, detail="Товар удален из корзины")
        else:
            old_quantity = cart_item.quantity
            cart_item.quantity = cart_item_update.quantity
            logger.info(f"Обновление количества: {old_quantity} -> {cart_item.quantity}")

    await db.commit()
    await db.refresh(cart_item)
    logger.info(f"Корзина обновлена: ID {cart_item.id}, новое количество: {cart_item.quantity}")

    # Теперь cart_item.product уже загружен через selectinload
    return cart_item


@router.delete("/remove")
async def remove_from_cart(
        product_id: int = Query(..., description="ID товара"),
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_async_db)
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

    # Получаем элемент корзины
    result = await db.execute(
        select(CartItem).where(
            CartItem.product_id == product_id,
            CartItem.user_id == user.id
        )
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        logger.warning(f"Товар с product_id {product_id} не найден в корзине пользователя {user.id}")
        return {"detail": "Товар отсутствовал в корзине", "product_id": product_id}

    logger.info(
        f"Найден товар в корзине: ID {cart_item.id}, product_id {cart_item.product_id}, quantity {cart_item.quantity}")

    await db.delete(cart_item)
    await db.commit()
    logger.info(f"Товар {product_id} успешно удален из корзины пользователя {telegram_id}")
    return {"detail": "Товар успешно удален из корзины", "product_id": product_id}


@router.delete("/clear")
async def clear_cart(
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_async_db)
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
    stmt = select(CartItem).where(CartItem.user_id == user.id)
    result = await db.execute(stmt)
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
        db: AsyncSession = Depends(get_async_db)
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
        db: AsyncSession = Depends(get_async_db)
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
        db: AsyncSession = Depends(get_async_db)
):
    """
    Получает количество уникальных товаров в корзине
    """
    user = await get_user_from_db(telegram_id, db)

    # Используем selectinload для загрузки продуктов
    stmt = select(CartItem).options(
        selectinload(CartItem.product)
    ).where(CartItem.user_id == user.id)

    result = await db.execute(stmt)
    cart_items = result.scalars().all()

    # Удаляем элементы с несуществующими продуктами
    valid_items = []
    for item in cart_items:
        if item.product:
            valid_items.append(item)
        else:
            # Удаляем элемент корзины без продукта
            await db.delete(item)

    if len(valid_items) < len(cart_items):
        await db.commit()

    total_items = sum(item.quantity for item in valid_items)
    unique_items = len(valid_items)

    return {
        "telegram_id": telegram_id,
        "unique_items": unique_items,
        "total_items": total_items,
        "cart_items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else "Неизвестно",
                "quantity": item.quantity,
                "price": item.product.price if item.product else 0
            }
            for item in valid_items
        ]
    }


# Endpoint для массового обновления корзины
@router.put("/batch-update")
async def batch_update_cart(
        updates: List[CartItemBatchUpdate],
        telegram_id: int = Query(..., description="Telegram ID пользователя"),
        db: AsyncSession = Depends(get_async_db)
):
    """
    Массовое обновление корзины
    """
    user = await get_user_from_db(telegram_id, db)
    results = []

    # Получаем текущую корзину с загруженными продуктами
    stmt = select(CartItem).options(
        selectinload(CartItem.product)
    ).where(CartItem.user_id == user.id)

    result = await db.execute(stmt)
    existing_items = {item.product_id: item for item in result.scalars().all()}

    for update in updates:
        cart_item = existing_items.get(update.product_id)

        if cart_item:
            if cart_item.product is None:
                # Продукт был удален из базы, удаляем запись из корзины
                logger.warning(
                    f"Продукт с ID {update.product_id} не найден в базе данных, элемент корзины будет удален")
                await db.delete(cart_item)
                results.append({
                    "product_id": update.product_id,
                    "status": "product_not_found_and_removed",
                    "message": "Продукт больше не доступен и был удален из корзины"
                })
            elif update.quantity and update.quantity > 0:
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
            # Проверяем, существует ли продукт
            product_result = await db.execute(
                select(Product).where(Product.id == update.product_id)
            )
            product = product_result.scalar_one_or_none()

            if update.quantity and update.quantity > 0 and product:
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
            elif update.quantity and update.quantity > 0 and not product:
                results.append({
                    "product_id": update.product_id,
                    "status": "product_not_found",
                    "message": "Продукт не найден в базе данных"
                })

    await db.commit()

    return {
        "telegram_id": telegram_id,
        "updates": results
    }