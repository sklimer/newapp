import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import yookassa
from yookassa import Configuration, Payment as YooPayment
import uuid
from datetime import datetime

from app.core.database import get_async_db
from app.core.config import settings
from app.core.security import get_current_user
from app.schemas.payments import Payment, PaymentCreate, PaymentUpdate, CreatePaymentRequest, PaymentResponse
from app.models.payments import Payment as PaymentModel
from app.models.orders import Order as OrderModel
from app.models.users import User as UserModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["payments"])

# Configure YooKassa
if settings.YOOKASSA_SHOP_ID and settings.YOOKASSA_API_KEY:
    Configuration.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_API_KEY)
else:
    logger.warning("⚠️ YooKassa credentials not configured. Payment processing will not work.")


@router.get("/", response_model=List[Payment])
async def get_payments(
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user),
        skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
        limit: int = Query(100, ge=1, le=100, description="Лимит записей"),
        order_id: Optional[int] = Query(None, description="Фильтр по ID заказа"),
):
    """
    Получить список платежей текущего пользователя
    """
    logger.info(f"💰 Получение платежей для пользователя {current_user_id}")

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

        logger.info(f"👤 Найден пользователь: {user.id}")

        # Строим запрос для платежей пользователя
        query = select(PaymentModel).where(
            PaymentModel.user_id == user.id
        )

        if order_id:
            query = query.where(PaymentModel.order_id == order_id)

        query = query.order_by(PaymentModel.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        payments = result.scalars().all()

        logger.info(f"✅ Найдено {len(payments)} платежей")
        return [Payment.from_orm(payment) for payment in payments]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при получении платежей: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении платежей"
        )


@router.get("/{payment_id}", response_model=Payment)
async def get_payment(
        payment_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Получить детальную информацию о платеже
    """
    logger.info(f"🔍 Получение платежа {payment_id} для пользователя {current_user_id}")

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

        # Находим платеж
        payment_result = await db.execute(
            select(PaymentModel).where(
                PaymentModel.id == payment_id,
                PaymentModel.user_id == user.id
            )
        )
        payment = payment_result.scalar_one_or_none()

        if not payment:
            logger.error(f"❌ Платеж {payment_id} не найден или доступ запрещен")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Платеж не найден"
            )

        logger.info(f"✅ Платеж {payment_id} успешно получен")
        return Payment.from_orm(payment)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при получении платежа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении платежа"
        )


@router.post("/", response_model=Payment)
async def create_payment(
        payment_create: PaymentCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Создать новый платеж
    """
    logger.info(f"🆕 Создание платежа для пользователя {current_user_id}")

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

        # Проверяем, что платеж создается для правильного пользователя
        if payment_create.user_id != user.id:
            logger.error(
                f"❌ Попытка создать платеж для другого пользователя. Текущий: {user.id}, запрошенный: {payment_create.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя создать платеж для другого пользователя"
            )

        # Проверяем существование заказа
        order_result = await db.execute(
            select(OrderModel).where(OrderModel.id == payment_create.order_id)
        )
        order = order_result.scalar_one_or_none()

        if not order:
            logger.error(f"❌ Заказ {payment_create.order_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )

        # Проверяем, что заказ принадлежит пользователю
        if order.user_id != user.id:
            logger.error(f"❌ Заказ {payment_create.order_id} не принадлежит пользователю {user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Заказ не принадлежит вам"
            )

        # Если метод платежа - бонусы, проверяем баланс
        if payment_create.payment_method == "BONUS":
            if user.bonus_balance < payment_create.amount:
                logger.error(
                    f"❌ Недостаточно бонусов. Требуется: {payment_create.amount}, доступно: {user.bonus_balance}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Недостаточно бонусов. Доступно: {user.bonus_balance}"
                )

        # Создаем платеж
        payment_data = payment_create.dict()
        payment_data["status"] = "pending"  # Начальный статус
        payment_data["created_at"] = datetime.utcnow()
        payment_data["updated_at"] = datetime.utcnow()

        db_payment = PaymentModel(**payment_data)
        db.add(db_payment)
        await db.commit()
        await db.refresh(db_payment)

        logger.info(f"✅ Платеж создан с ID: {db_payment.id}")

        return Payment.from_orm(db_payment)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Ошибка при создании платежа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании платежа"
        )


@router.put("/{payment_id}", response_model=Payment)
async def update_payment(
        payment_id: int,
        payment_update: PaymentUpdate,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Обновить платеж
    """
    logger.info(f"✏️ Обновление платежа {payment_id} для пользователя {current_user_id}")

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

        # Находим платеж
        payment_result = await db.execute(
            select(PaymentModel).where(
                PaymentModel.id == payment_id,
                PaymentModel.user_id == user.id
            )
        )
        payment = payment_result.scalar_one_or_none()

        if not payment:
            logger.error(f"❌ Платеж {payment_id} не найден или доступ запрещен")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Платеж не найден"
            )

        # Обновляем только переданные поля
        update_data = payment_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        await db.execute(
            update(PaymentModel)
            .where(PaymentModel.id == payment_id)
            .values(**update_data)
        )

        await db.commit()

        # Получаем обновленный платеж
        payment_result = await db.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        updated_payment = payment_result.scalar_one()

        logger.info(f"✅ Платеж {payment_id} успешно обновлен")

        return Payment.from_orm(updated_payment)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Ошибка при обновлении платежа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении платежа"
        )


@router.post("/create-yookassa-payment", response_model=PaymentResponse)
async def create_yookassa_payment(
        request_data: CreatePaymentRequest,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Создать платеж через YooKassa
    """
    logger.info(f"💳 Создание YooKassa платежа для пользователя {current_user_id}")

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

        # Проверяем существование заказа
        order_result = await db.execute(
            select(OrderModel).where(OrderModel.id == request_data.order_id)
        )
        order = order_result.scalar_one_or_none()

        if not order:
            logger.error(f"❌ Заказ {request_data.order_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )

        # Проверяем, что заказ принадлежит пользователю
        if order.user_id != user.id:
            logger.error(f"❌ Заказ {request_data.order_id} не принадлежит пользователю {user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Заказ не принадлежит вам"
            )

        # Проверяем, не оплачен ли уже заказ
        if order.payment_status == "paid":
            logger.error(f"❌ Заказ {request_data.order_id} уже оплачен")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Заказ уже оплачен"
            )

        # Проверяем конфигурацию YooKassa
        if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_API_KEY:
            logger.error("❌ YooKassa не настроен")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Платежная система не настроена"
            )

        # Создаем платеж в YooKassa
        idempotence_key = str(uuid.uuid4())

        payment_request = {
            "amount": {
                "value": f"{request_data.amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": request_data.return_url or settings.FRONTEND_URL or "https://t.me/"
            },
            "capture": True,
            "description": f"Оплата заказа #{order.order_number}",
            "metadata": {
                "order_id": request_data.order_id,
                "user_id": user.id,
                "order_number": order.order_number
            }
        }

        logger.info(f"🔄 Создание платежа YooKassa: {payment_request}")

        try:
            yookassa_payment = YooPayment.create(payment_request, idempotence_key)
            logger.info(f"✅ YooKassa платеж создан: {yookassa_payment.id}")

            # Сохраняем платеж в базе данных
            payment_data = {
                "order_id": request_data.order_id,
                "user_id": user.id,
                "payment_method": "YOOKASSA",
                "amount": request_data.amount,
                "status": yookassa_payment.status,
                "provider_payment_id": yookassa_payment.id,
                "provider_response": str(yookassa_payment),
                "description": f"Оплата заказа #{order.order_number} через YooKassa",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            db_payment = PaymentModel(**payment_data)
            db.add(db_payment)
            await db.commit()
            await db.refresh(db_payment)

            logger.info(f"✅ Платеж сохранен в БД с ID: {db_payment.id}")

            return PaymentResponse(
                payment_id=yookassa_payment.id,
                payment_url=yookassa_payment.confirmation.confirmation_url,
                status=yookassa_payment.status,
                order_id=request_data.order_id,
                amount=request_data.amount
            )

        except Exception as e:
            logger.error(f"❌ Ошибка YooKassa: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании платежа: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при создании YooKassa платежа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка при создании платежа"
        )


@router.post("/yookassa-webhook")
async def yookassa_webhook(
        request: Request,
        db: AsyncSession = Depends(get_async_db)
):
    """
    Обработка вебхука от YooKassa
    """
    logger.info("🔔 Получен вебхук от YooKassa")

    try:
        # Получаем данные вебхука
        payload = await request.json()
        logger.info(f"📦 Данные вебхука: {payload}")

        event_type = payload.get('event')
        payment_data = payload.get('object', {})
        payment_id = payment_data.get('id')

        if not payment_id:
            logger.error("❌ Отсутствует payment_id в вебхуке")
            return {"status": "error", "message": "Missing payment_id"}

        logger.info(f"🔍 Обработка события: {event_type}, платеж: {payment_id}")

        # Находим платеж в базе данных
        payment_result = await db.execute(
            select(PaymentModel).where(PaymentModel.provider_payment_id == payment_id)
        )
        payment = payment_result.scalar_one_or_none()

        if not payment:
            logger.error(f"❌ Платеж {payment_id} не найден в базе данных")
            return {"status": "error", "message": "Payment not found"}

        # Обрабатываем разные события
        if event_type == 'payment.succeeded':
            # Обновляем статус платежа
            await db.execute(
                update(PaymentModel)
                .where(PaymentModel.id == payment.id)
                .values(
                    status='succeeded',
                    updated_at=datetime.utcnow()
                )
            )

            # Обновляем статус заказа
            if payment.order_id:
                await db.execute(
                    update(OrderModel)
                    .where(OrderModel.id == payment.order_id)
                    .values(
                        payment_status='paid',
                        updated_at=datetime.utcnow()
                    )
                )

                logger.info(f"✅ Заказ {payment.order_id} отмечен как оплаченный")

            logger.info(f"✅ Платеж {payment_id} успешно обработан")

        elif event_type == 'payment.waiting_for_capture':
            await db.execute(
                update(PaymentModel)
                .where(PaymentModel.id == payment.id)
                .values(
                    status='waiting_for_capture',
                    updated_at=datetime.utcnow()
                )
            )
            logger.info(f"🔄 Платеж {payment_id} ожидает подтверждения")

        elif event_type == 'payment.canceled':
            await db.execute(
                update(PaymentModel)
                .where(PaymentModel.id == payment.id)
                .values(
                    status='cancelled',
                    updated_at=datetime.utcnow()
                )
            )
            logger.info(f"❌ Платеж {payment_id} отменен")

        else:
            logger.info(f"ℹ️ Игнорируем событие: {event_type}")
            return {"status": "ignored", "event": event_type}

        await db.commit()

        # Отправляем ответ YooKassa
        return {"status": "ok", "event": event_type, "payment_id": payment_id}

    except Exception as e:
        logger.error(f"❌ Ошибка обработки вебхука: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.post("/process-bonus-payment", response_model=Payment)
async def process_bonus_payment(
        order_id: int,
        amount: float,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Обработать платеж бонусами
    """
    logger.info(f"🎁 Обработка бонусного платежа для заказа {order_id}, сумма: {amount}")

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

        logger.info(f"👤 Пользователь найден. Баланс бонусов: {user.bonus_balance}")

        # Проверяем заказ
        order_result = await db.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        order = order_result.scalar_one_or_none()

        if not order:
            logger.error(f"❌ Заказ {order_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )

        # Проверяем, что заказ принадлежит пользователю
        if order.user_id != user.id:
            logger.error(f"❌ Заказ {order_id} не принадлежит пользователю {user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Заказ не принадлежит вам"
            )

        # Проверяем баланс бонусов
        if user.bonus_balance < amount:
            logger.error(f"❌ Недостаточно бонусов. Требуется: {amount}, доступно: {user.bonus_balance}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недостаточно бонусов. Доступно: {user.bonus_balance}"
            )

        # Проверяем, не оплачен ли уже заказ
        if order.payment_status == "paid":
            logger.error(f"❌ Заказ {order_id} уже оплачен")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Заказ уже оплачен"
            )

        # Создаем запись о платеже
        payment_data = {
            "order_id": order_id,
            "user_id": user.id,
            "payment_method": "BONUS",
            "amount": amount,
            "status": "succeeded",
            "description": f"Оплата заказа #{order.order_number} бонусами",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        db_payment = PaymentModel(**payment_data)
        db.add(db_payment)

        # Списываем бонусы
        await db.execute(
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(
                bonus_balance=UserModel.bonus_balance - amount,
                updated_at=datetime.utcnow()
            )
        )

        # Обновляем статус заказа
        await db.execute(
            update(OrderModel)
            .where(OrderModel.id == order_id)
            .values(
                payment_status='paid',
                updated_at=datetime.utcnow()
            )
        )

        await db.commit()
        await db.refresh(db_payment)

        logger.info(f"✅ Бонусный платеж успешно обработан. Новый баланс: {user.bonus_balance - amount}")

        return Payment.from_orm(db_payment)

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Ошибка при обработке бонусного платежа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке бонусного платежа"
        )


@router.get("/check-payment/{provider_payment_id}")
async def check_payment_status(
        provider_payment_id: str,
        db: AsyncSession = Depends(get_async_db),
        current_user_id: str = Depends(get_current_user)
):
    """
    Проверить статус платежа YooKassa
    """
    logger.info(f"🔍 Проверка статуса платежа YooKassa: {provider_payment_id}")

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

        # Находим платеж в базе данных
        payment_result = await db.execute(
            select(PaymentModel).where(
                PaymentModel.provider_payment_id == provider_payment_id,
                PaymentModel.user_id == user.id
            )
        )
        payment = payment_result.scalar_one_or_none()

        if not payment:
            logger.error(f"❌ Платеж {provider_payment_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Платеж не найден"
            )

        # Если платеж через YooKassa, проверяем актуальный статус
        if payment.payment_method == "YOOKASSA":
            try:
                yookassa_payment = YooPayment.find_one(provider_payment_id)

                # Обновляем статус в базе данных, если он изменился
                if yookassa_payment.status != payment.status:
                    await db.execute(
                        update(PaymentModel)
                        .where(PaymentModel.id == payment.id)
                        .values(
                            status=yookassa_payment.status,
                            updated_at=datetime.utcnow()
                        )
                    )

                    # Если платеж успешен, обновляем статус заказа
                    if yookassa_payment.status == 'succeeded' and payment.order_id:
                        await db.execute(
                            update(OrderModel)
                            .where(OrderModel.id == payment.order_id)
                            .values(
                                payment_status='paid',
                                updated_at=datetime.utcnow()
                            )
                        )

                    await db.commit()

                    logger.info(f"✅ Статус платежа обновлен: {payment.status} -> {yookassa_payment.status}")

                return {
                    "payment_id": provider_payment_id,
                    "status": yookassa_payment.status,
                    "amount": payment.amount,
                    "order_id": payment.order_id,
                    "updated": yookassa_payment.status != payment.status
                }

            except Exception as e:
                logger.error(f"❌ Ошибка при проверке статуса в YooKassa: {e}")
                # Возвращаем статус из базы данных
                return {
                    "payment_id": provider_payment_id,
                    "status": payment.status,
                    "amount": payment.amount,
                    "order_id": payment.order_id,
                    "note": "Статус из базы данных (ошибка запроса к YooKassa)"
                }

        # Для других методов платежа возвращаем статус из базы данных
        return {
            "payment_id": provider_payment_id,
            "status": payment.status,
            "amount": payment.amount,
            "order_id": payment.order_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке статуса платежа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при проверке статуса платежа"
        )