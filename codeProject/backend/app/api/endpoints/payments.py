from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import yookassa
from yookassa import Configuration, Payment as YooPayment
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.schemas.payments import Payment, PaymentCreate, PaymentUpdate, CreatePaymentRequest, PaymentResponse
from app.models.payments import Payment as PaymentModel
from app.models.orders import Order as OrderModel
from app.models.users import User as UserModel

router = APIRouter()

# Configure YooKassa
Configuration.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_API_KEY)


@router.get("/", response_model=List[Payment])
async def get_payments(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    order_id: int = None
):
    """Get all payments with optional filters"""
    query = PaymentModel.__table__.select()
    
    if user_id:
        query = query.where(PaymentModel.user_id == user_id)
    if order_id:
        query = query.where(PaymentModel.order_id == order_id)
    
    query = query.order_by(PaymentModel.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    payments = result.fetchall()
    return [Payment.from_orm(row) for row in payments]


@router.get("/{payment_id}", response_model=Payment)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific payment by ID"""
    result = await db.execute(
        PaymentModel.__table__.select()
        .where(PaymentModel.id == payment_id)
    )
    payment = result.fetchone()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return Payment.from_orm(payment)


@router.post("/", response_model=Payment)
async def create_payment(
    payment: PaymentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new payment"""
    # Validate order exists
    order_result = await db.execute(
        OrderModel.__table__.select()
        .where(OrderModel.id == payment.order_id)
    )
    order = order_result.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate user exists
    user_result = await db.execute(
        UserModel.__table__.select()
        .where(UserModel.id == payment.user_id)
    )
    user = user_result.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If payment method is bonus, verify user has enough bonus balance
    if payment.payment_method == "BONUS":
        if user.bonus_balance < payment.amount:
            raise HTTPException(status_code=400, detail="Insufficient bonus balance")
    
    db_payment = PaymentModel(**payment.dict())
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    return Payment.from_orm(db_payment)


@router.put("/{payment_id}", response_model=Payment)
async def update_payment(
    payment_id: int,
    payment_update: PaymentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a payment"""
    result = await db.execute(
        PaymentModel.__table__.select()
        .where(PaymentModel.id == payment_id)
    )
    db_payment = result.fetchone()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    update_data = payment_update.dict(exclude_unset=True)
    await db.execute(
        PaymentModel.__table__.update()
        .where(PaymentModel.id == payment_id)
        .values(**update_data)
    )
    await db.commit()
    
    result = await db.execute(
        PaymentModel.__table__.select()
        .where(PaymentModel.id == payment_id)
    )
    updated_payment = result.fetchone()
    return Payment.from_orm(updated_payment)


@router.post("/create-yookassa-payment")
async def create_yookassa_payment(
    request_data: CreatePaymentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a YooKassa payment"""
    # Validate order exists
    order_result = await db.execute(
        OrderModel.__table__.select()
        .where(OrderModel.id == request_data.order_id)
    )
    order = order_result.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Create YooKassa payment
    idempotence_key = str(uuid.uuid4())
    
    payment_request = {
        "amount": {
            "value": str(request_data.amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": request_data.return_url or "https://your-frontend.vercel.app"
        },
        "capture": True,
        "description": f"Payment for order {order.order_number}",
        "metadata": {
            "order_id": request_data.order_id,
            "user_id": order.user_id
        }
    }
    
    try:
        yookassa_payment = YooPayment.create(payment_request, idempotence_key)
        
        # Save payment record to database
        payment_data = {
            "order_id": request_data.order_id,
            "user_id": order.user_id,
            "payment_method": "YOOKASSA",
            "amount": request_data.amount,
            "status": yookassa_payment.status,
            "provider_payment_id": yookassa_payment.id,
            "provider_response": str(yookassa_payment),
            "description": f"Payment for order {order.order_number}"
        }
        
        db_payment = PaymentModel(**payment_data)
        db.add(db_payment)
        await db.commit()
        await db.refresh(db_payment)
        
        return PaymentResponse(
            payment_id=yookassa_payment.id,
            payment_url=yookassa_payment.confirmation.confirmation_url,
            status=yookassa_payment.status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating YooKassa payment: {str(e)}")


@router.post("/yookassa-webhook")
async def yookassa_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle YooKassa webhook"""
    try:
        # Get the JSON payload from the request
        payload = await request.json()
        
        # Process the webhook event
        event_type = payload.get('event')
        payment_data = payload.get('object', {})
        payment_id = payment_data.get('id')
        
        if event_type == 'payment.succeeded':
            # Update payment status in database
            await db.execute(
                PaymentModel.__table__.update()
                .where(PaymentModel.provider_payment_id == payment_id)
                .values(status='succeeded')
            )
            
            # Update order status to paid
            order_id = payment_data.get('metadata', {}).get('order_id')
            if order_id:
                await db.execute(
                    OrderModel.__table__.update()
                    .where(OrderModel.id == order_id)
                    .values(payment_status='paid')
                )
            
            await db.commit()
            return {"status": "ok"}
        
        elif event_type == 'payment.waiting_for_capture':
            # Update payment status in database
            await db.execute(
                PaymentModel.__table__.update()
                .where(PaymentModel.provider_payment_id == payment_id)
                .values(status='processing')
            )
            await db.commit()
            return {"status": "ok"}
        
        elif event_type == 'payment.canceled':
            # Update payment status in database
            await db.execute(
                PaymentModel.__table__.update()
                .where(PaymentModel.provider_payment_id == payment_id)
                .values(status='cancelled')
            )
            await db.commit()
            return {"status": "ok"}
        
        return {"status": "ignored"}
    
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


@router.post("/process-bonus-payment")
async def process_bonus_payment(
    order_id: int,
    user_id: int,
    amount: float,
    db: AsyncSession = Depends(get_db)
):
    """Process a bonus payment"""
    # Validate order exists
    order_result = await db.execute(
        OrderModel.__table__.select()
        .where(OrderModel.id == order_id)
    )
    order = order_result.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate user exists and has enough bonus balance
    user_result = await db.execute(
        UserModel.__table__.select()
        .where(UserModel.id == user_id)
    )
    user = user_result.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.bonus_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient bonus balance")
    
    # Create payment record
    payment_data = {
        "order_id": order_id,
        "user_id": user_id,
        "payment_method": "BONUS",
        "amount": amount,
        "status": "succeeded",
        "description": f"Bonus payment for order {order.order_number}"
    }
    
    db_payment = PaymentModel(**payment_data)
    db.add(db_payment)
    
    # Deduct bonus from user
    await db.execute(
        UserModel.__table__.update()
        .where(UserModel.id == user_id)
        .values(bonus_balance=UserModel.bonus_balance - amount)
    )
    
    # Update order payment status
    await db.execute(
        OrderModel.__table__.update()
        .where(OrderModel.id == order_id)
        .values(payment_status='paid')
    )
    
    await db.commit()
    return Payment.from_orm(db_payment)