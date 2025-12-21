from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.orm import declarative_base

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    YOOKASSA = "yookassa"
    CASH = "cash"
    CARD = "card"


class Payment(Base):
    __tablename__ = "payments"

    id: int = Column(Integer, primary_key=True, index=True)
    order_id: int = Column(Integer, ForeignKey("orders.id"), nullable=False)
    payment_method: PaymentMethod = Column(Enum(PaymentMethod), nullable=False)
    status: PaymentStatus = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    amount: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)
    currency: str = Column(String, default="RUB")
    
    # YooKassa specific fields
    yookassa_payment_id: Optional[str] = Column(String, nullable=True)  # YooKassa payment ID
    yookassa_status: Optional[str] = Column(String, nullable=True)  # Status from YooKassa
    yookassa_confirmation_url: Optional[str] = Column(String, nullable=True)  # URL for payment confirmation
    
    # Transaction information
    transaction_id: Optional[str] = Column(String, nullable=True)  # External transaction ID
    gateway_response: Optional[dict] = Column(Text, nullable=True)  # Raw response from payment gateway
    
    # Customer information
    customer_email: Optional[str] = Column(String, nullable=True)
    customer_phone: Optional[str] = Column(String, nullable=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    processed_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    order = relationship("Order", back_populates="payments")


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_refunded = Column(Boolean, default=False)
    refund_amount = Column(Numeric(10, 2))
    refund_reason = Column(String(255))
    yookassa_payment_id = Column(String(255))
    yookassa_receipt_id = Column(String(255))