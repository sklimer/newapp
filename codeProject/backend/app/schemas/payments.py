from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    YOOKASSA = "yookassa"
    CASH = "cash"
    BONUS = "bonus"


class PaymentBase(BaseModel):
    order_id: int
    user_id: int
    payment_method: PaymentMethod
    amount: float
    currency: str = "RUB"
    description: Optional[str] = None
    metadata: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    provider_payment_id: Optional[str] = None
    provider_response: Optional[str] = None


class Payment(PaymentBase):
    id: int
    payment_provider: Optional[str] = None
    provider_payment_id: Optional[str] = None
    status: PaymentStatus
    refunded: bool = False
    refunded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CreatePaymentRequest(BaseModel):
    order_id: int
    amount: float
    payment_method: str
    return_url: Optional[str] = None  # For redirect after payment


class PaymentResponse(BaseModel):
    payment_id: str
    payment_url: Optional[str] = None
    status: str