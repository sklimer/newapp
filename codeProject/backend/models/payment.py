from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from ..database import metadata
from enum import Enum as PyEnum


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, PyEnum):
    YOOKASSA = "yookassa"
    CASH = "cash"
    BONUS = "bonus"


class Payment:
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_provider = Column(String, nullable=True)  # For external providers like Yookassa
    provider_payment_id = Column(String, nullable=True)  # Payment ID from the provider
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    currency = Column(String, default="RUB")
    description = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    provider_response = Column(Text, nullable=True)  # Raw response from payment provider
    refunded = Column(Boolean, default=False)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Transaction:
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # "payment", "refund", "bonus_usage", "bonus_accrual"
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    balance_before = Column(Numeric(precision=10, scale=2), nullable=False)
    balance_after = Column(Numeric(precision=10, scale=2), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())