from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import metadata


class BonusProgram:
    __tablename__ = "bonus_programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Registration Bonus", "Order Bonus"
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False)  # "registration", "order_percent", "fixed_amount", "referral"
    value = Column(Numeric(precision=10, scale=2), nullable=False)  # Bonus amount or percentage
    min_order_amount = Column(Numeric(precision=10, scale=2), nullable=True)  # Minimum order to earn bonus
    max_bonus_amount = Column(Numeric(precision=10, scale=2), nullable=True)  # Max bonus for percentage-based
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # If True, this is the default bonus program
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class BonusTransaction:
    __tablename__ = "bonus_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("bonus_programs.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # Nullable for registration bonuses
    amount = Column(Numeric(precision=10, scale=2), nullable=False)  # Positive for earned, negative for used
    balance_before = Column(Numeric(precision=10, scale=2), nullable=False)
    balance_after = Column(Numeric(precision=10, scale=2), nullable=False)
    description = Column(Text, nullable=True)
    transaction_type = Column(String, nullable=False)  # "earned", "used", "referral_bonus"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())