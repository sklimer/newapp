from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ... import models, schemas

router = APIRouter()


@router.post("/payments/create/", response_model=schemas.Payment)
async def create_payment(payment: schemas.PaymentCreate, db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass


@router.get("/payments/{payment_id}", response_model=schemas.Payment)
async def get_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass


@router.post("/payments/yookassa/webhook/")
async def yookassa_webhook():
    # Handle Yookassa webhook
    pass