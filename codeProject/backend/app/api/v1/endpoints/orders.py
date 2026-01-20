import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import datetime
import uuid

from app.core.database import get_async_db
from app.core.security import require_telegram_auth, get_current_user
from app.schemas.orders import Order, OrderCreate, OrderUpdate, OrderItem, OrderItemCreate
from app.models.orders import Order as OrderModel, OrderItem as OrderItemModel
from app.models.users import User as UserModel
from app.models.menu import Product as ProductModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[Order])
async def get_orders(
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user),
        skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
        limit: int = Query(100, ge=1, le=100, description="Лимит записей"),
        status: Optional[str] = Query(None, description="Фильтр по статусу заказа")
):
    """
    Получить список заказов текущего пользователя
    """
    logger.info(f"📋 Получение заказов для пользователя {current_user_id}")

    try:
        # Находим пользователя в базе по telegram_id
        user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            logger.error(f"❌ Пользователь с telegram_id={current_user_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        logger.info(f"👤 Найден пользователь: {user.id}, telegram_id: {user.telegram_id}")

        # Строим запрос для заказов пользователя
        query = select(OrderModel).where(
            OrderModel.user_id == user.id,
            OrderModel.is_active == True
        )

        if status:
            query = query.where(OrderModel.status == status)

        query = query.order_by(OrderModel.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        orders = result.scalars().all()

        logger.info(f"✅ Найдено {len(orders)} заказов")

        # Преобразуем в схему
        orders_list = []
        for order in orders:
            order_dict = Order.from_orm(order).dict()

            # Получаем элементы заказа
            items_result = await db.execute(
                select(OrderItemModel).where(OrderItemModel.order_id == order.id)
            )
            items = items_result.scalars().all()
            order_dict["order_items"] = [OrderItem.from_orm(item) for item in items]

            orders_list.append(order_dict)

        return orders_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при получении заказов: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении заказов"
        )


@router.get("/{order_id}", response_model=Order)
async def get_order(
        order_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Получить детальную информацию о заказе
    """
    logger.info(f"🔍 Получение заказа {order_id} для пользователя {current_user_id}")

    try:
        # Находим пользователя
        user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            logger.error(f"❌ Пользователь с telegram_id={current_user_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Находим заказ
        order_result = await db.execute(
            select(OrderModel).where(
                OrderModel.id == order_id,
                OrderModel.user_id == user.id,
                OrderModel.is_active == True
            )
        )
        order = order_result.scalar_one_or_none()

        if not order:
            logger.error(f"❌ Заказ {order_id} не найден или доступ запрещен")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )

        # Получаем элементы заказа
        items_result = await db.execute(
            select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        )
        items = items_result.scalars().all()

        # Преобразуем в схему
        order_dict = Order.from_orm(order).dict()
        order_dict["order_items"] = [OrderItem.from_orm(item) for item in items]

        logger.info(f"✅ Заказ {order_id} успешно получен")

        return order_dict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при получении заказа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении заказа"
        )


@router.post("/", response_model=Order)
async def create_order(
        order_create: OrderCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Создать новый заказ
    """
    logger.info(f"🆕 Создание заказа для пользователя {current_user_id}")
    logger.debug(f"📝 Данные заказа: {order_create.dict()}")

    try:
        # Находим пользователя
        user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            logger.error(f"❌ Пользователь с telegram_id={current_user_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        logger.info(f"👤 Пользователь найден: {user.id}, баланс бонусов: {user.bonus_balance}")

        # Проверяем баланс бонусов
        if order_create.bonus_used > user.bonus_balance:
            logger.error(
                f"❌ Недостаточно бонусов. Требуется: {order_create.bonus_used}, доступно: {user.bonus_balance}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недостаточно бонусов. Доступно: {user.bonus_balance}"
            )

        # Проверяем продукты в заказе
        order_items_data = []
        total_amount = 0

        for item in order_create.order_items:
            # Проверяем существование продукта
            product_result = await db.execute(
                select(ProductModel).where(
                    ProductModel.id == item.product_id,
                    ProductModel.is_active == True
                )
            )
            product = product_result.scalar_one_or_none()

            if not product:
                logger.error(f"❌ Продукт {item.product_id} не найден")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Продукт с ID {item.product_id} не найден"
                )

            # Проверяем наличие
            if product.stock_quantity is not None and item.quantity > product.stock_quantity:
                logger.error(
                    f"❌ Недостаточно товара {product.name}. Требуется: {item.quantity}, в наличии: {product.stock_quantity}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Недостаточно товара '{product.name}'. В наличии: {product.stock_quantity}"
                )

            # Рассчитываем стоимость позиции
            item_price = item.price if item.price is not None else product.price
            item_total = item_price * item.quantity
            total_amount += item_total

            order_items_data.append({
                "product_id": item.product_id,
                "product_name": product.name,
                "quantity": item.quantity,
                "price": item_price,
                "total_price": item_total,
                "note": item.note
            })

        logger.info(f"💰 Общая сумма заказа: {total_amount}")
        logger.info(f"🎁 Использовано бонусов: {order_create.bonus_used}")

        # Рассчитываем финальную сумму
        final_amount = max(0, total_amount - order_create.bonus_used)
        logger.info(f"💰 Финальная сумма к оплате: {final_amount}")

        # Генерируем номер заказа
        order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4().int)[:6]}"

        # Создаем заказ
        order_data = order_create.dict(exclude={"order_items"})
        order_data.update({
            "user_id": user.id,
            "order_number": order_number,
            "total_amount": total_amount,
            "final_amount": final_amount,
            "payment_status": "pending",
            "status": "new",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })

        db_order = OrderModel(**order_data)
        db.add(db_order)
        await db.flush()  # Получаем ID заказа

        logger.info(f"✅ Заказ создан с ID: {db_order.id}, номер: {order_number}")

        # Создаем элементы заказа
        for item_data in order_items_data:
            order_item = OrderItemModel(
                order_id=db_order.id,
                **item_data
            )
            db.add(order_item)

            # Обновляем количество на складе
            if product.stock_quantity is not None:
                await db.execute(
                    update(ProductModel)
                    .where(ProductModel.id == item_data["product_id"])
                    .values(stock_quantity=ProductModel.stock_quantity - item_data["quantity"])
                )

        # Обновляем статистику пользователя
        if order_create.bonus_used > 0:
            new_bonus_balance = user.bonus_balance - order_create.bonus_used
            await db.execute(
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(
                    bonus_balance=new_bonus_balance,
                    order_count=UserModel.order_count + 1,
                    total_spent=UserModel.total_spent + final_amount,
                    updated_at=datetime.utcnow()
                )
            )
        else:
            await db.execute(
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(
                    order_count=UserModel.order_count + 1,
                    total_spent=UserModel.total_spent + final_amount,
                    updated_at=datetime.utcnow()
                )
            )

        # Фиксируем изменения
        await db.commit()
        await db.refresh(db_order)

        # Получаем полные данные заказа для ответа
        order_result = await db.execute(
            select(OrderModel).where(OrderModel.id == db_order.id)
        )
        created_order = order_result.scalar_one()

        # Получаем элементы заказа
        items_result = await db.execute(
            select(OrderItemModel).where(OrderItemModel.order_id == db_order.id)
        )
        items = items_result.scalars().all()

        # Формируем ответ
        order_dict = Order.from_orm(created_order).dict()
        order_dict["order_items"] = [OrderItem.from_orm(item) for item in items]

        logger.info(f"✅ Заказ {db_order.id} успешно создан. Финальная сумма: {final_amount}")

        return order_dict

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Ошибка при создании заказа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании заказа"
        )


@router.put("/{order_id}", response_model=Order)
async def update_order(
        order_id: int,
        order_update: OrderUpdate,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Обновить заказ (только определенные поля)
    """
    logger.info(f"✏️ Обновление заказа {order_id} для пользователя {current_user_id}")

    try:
        # Находим пользователя
        user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            logger.error(f"❌ Пользователь с telegram_id={current_user_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Находим заказ
        order_result = await db.execute(
            select(OrderModel).where(
                OrderModel.id == order_id,
                OrderModel.user_id == user.id,
                OrderModel.is_active == True
            )
        )
        order = order_result.scalar_one_or_none()

        if not order:
            logger.error(f"❌ Заказ {order_id} не найден или доступ запрещен")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )

        # Проверяем, можно ли обновлять заказ
        if order.status not in ["new", "pending"]:
            logger.error(f"❌ Заказ {order_id} в статусе {order.status} нельзя обновить")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Заказ нельзя обновить в текущем статусе"
            )

        # Обновляем только переданные поля
        update_data = order_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        await db.execute(
            update(OrderModel)
            .where(OrderModel.id == order_id)
            .values(**update_data)
        )

        await db.commit()

        # Получаем обновленный заказ
        order_result = await db.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        updated_order = order_result.scalar_one()

        logger.info(f"✅ Заказ {order_id} успешно обновлен")

        return Order.from_orm(updated_order)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Ошибка при обновлении заказа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении заказа"
        )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
        order_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Отменить заказ (мягкое удаление)
    """
    logger.info(f"🗑️ Отмена заказа {order_id} для пользователя {current_user_id}")

    try:
        # Находим пользователя
        user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            logger.error(f"❌ Пользователь с telegram_id={current_user_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Находим заказ
        order_result = await db.execute(
            select(OrderModel).where(
                OrderModel.id == order_id,
                OrderModel.user_id == user.id,
                OrderModel.is_active == True
            )
        )
        order = order_result.scalar_one_or_none()

        if not order:
            logger.error(f"❌ Заказ {order_id} не найден или доступ запрещен")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )

        # Проверяем, можно ли отменить заказ
        if order.status not in ["new", "pending"]:
            logger.error(f"❌ Заказ {order_id} в статусе {order.status} нельзя отменить")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Заказ нельзя отменить в текущем статусе"
            )

        # Обновляем статус заказа
        await db.execute(
            update(OrderModel)
            .where(OrderModel.id == order_id)
            .values(
                status="cancelled",
                is_active=False,
                updated_at=datetime.utcnow()
            )
        )

        # Возвращаем бонусы, если они были использованы
        if order.bonus_used > 0:
            await db.execute(
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(bonus_balance=UserModel.bonus_balance + order.bonus_used)
            )

        # Возвращаем товары на склад
        items_result = await db.execute(
            select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        )
        items = items_result.scalars().all()

        for item in items:
            await db.execute(
                update(ProductModel)
                .where(ProductModel.id == item.product_id)
                .values(stock_quantity=ProductModel.stock_quantity + item.quantity)
            )

        await db.commit()

        logger.info(f"✅ Заказ {order_id} успешно отменен")

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Ошибка при отмене заказа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отмене заказа"
        )


@router.get("/{order_id}/items", response_model=List[OrderItem])
async def get_order_items(
        order_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Получить элементы заказа
    """
    logger.info(f"📦 Получение элементов заказа {order_id} для пользователя {current_user_id}")

    try:
        # Находим пользователя
        user_result = await db.execute(
            select(UserModel).where(UserModel.telegram_id == current_user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            logger.error(f"❌ Пользователь с telegram_id={current_user_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Проверяем доступ к заказу
        order_result = await db.execute(
            select(OrderModel).where(
                OrderModel.id == order_id,
                OrderModel.user_id == user.id,
                OrderModel.is_active == True
            )
        )
        order = order_result.scalar_one_or_none()

        if not order:
            logger.error(f"❌ Заказ {order_id} не найден или доступ запрещен")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )

        # Получаем элементы заказа
        items_result = await db.execute(
            select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        )
        items = items_result.scalars().all()

        logger.info(f"✅ Найдено {len(items)} элементов заказа")

        return [OrderItem.from_orm(item) for item in items]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при получении элементов заказа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении элементов заказа"
        )