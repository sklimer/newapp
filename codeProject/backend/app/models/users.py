from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    telegram_id: str = Column(String, unique=True, index=True, nullable=False)
    username: Optional[str] = Column(String, unique=True, index=True, nullable=True)
    first_name: Optional[str] = Column(String, nullable=True)
    last_name: Optional[str] = Column(String, nullable=True)
    phone_number: Optional[str] = Column(String, index=True, nullable=True)
    email: Optional[str] = Column(String, index=True, nullable=True)
    address_lat: Optional[Decimal] = Column(Numeric(precision=9, scale=6), nullable=True)
    address_lon: Optional[Decimal] = Column(Numeric(precision=9, scale=6), nullable=True)
    address_description: Optional[str] = Column(Text, nullable=True)
    bonus_balance: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)
    total_spent: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)
    order_count: int = Column(Integer, default=0)
    is_active: bool = Column(Boolean, default=True)
    is_blocked: bool = Column(Boolean, default=False)
    is_admin: bool = Column(Boolean, default=False)
    referral_code: Optional[str] = Column(String, unique=True, index=True, nullable=True)
    referred_by: Optional[int] = Column(Integer, nullable=True)  # ID of the user who referred this user
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    orders = relationship("Order", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    bonuses = relationship("BonusTransaction", back_populates="user")