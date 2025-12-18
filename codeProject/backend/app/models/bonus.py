from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BonusTransactionType(str, enum.Enum):
    EARNED = "earned"
    SPENT = "spent"
    REFUNDED = "refunded"


class BonusTransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BonusTransaction(Base):
    __tablename__ = "bonus_transactions"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id: Optional[int] = Column(Integer, ForeignKey("orders.id"), nullable=True)
    transaction_type: BonusTransactionType = Column(Enum(BonusTransactionType), nullable=False)
    status: BonusTransactionStatus = Column(Enum(BonusTransactionStatus), default=BonusTransactionStatus.COMPLETED)
    amount: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # bonus amount
    description: Optional[str] = Column(String, nullable=True)  # reason for bonus transaction
    expires_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)  # when bonus expires
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="bonuses")
    order = relationship("Order")


class Referral(Base):
    __tablename__ = "referrals"

    id: int = Column(Integer, primary_key=True, index=True)
    referrer_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)  # user who referred
    referee_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)  # user who was referred
    bonus_amount: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # bonus given for referral
    is_claimed: bool = Column(Boolean, default=False)  # whether bonus has been claimed
    claimed_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_id])
    referee = relationship("User", foreign_keys=[referee_id])


class BonusRule(Base):
    __tablename__ = "bonus_rules"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False)  # e.g., "Registration bonus", "Order percentage"
    description: Optional[str] = Column(Text, nullable=True)
    rule_type: str = Column(String, nullable=False)  # e.g., "registration", "percentage", "fixed_amount"
    value: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # percentage or fixed amount
    applies_to_new_users: bool = Column(Boolean, default=False)  # whether rule applies to new users only
    min_order_amount: Optional[Decimal] = Column(Numeric(precision=10, scale=2), nullable=True)  # min order for rule to apply
    max_bonus_amount: Optional[Decimal] = Column(Numeric(precision=10, scale=2), nullable=True)  # max bonus that can be earned
    validity_days: Optional[int] = Column(Integer, nullable=True)  # how many days bonus is valid
    is_active: bool = Column(Boolean, default=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())