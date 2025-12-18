from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric
from sqlalchemy.sql import func
from ..database import metadata


class User:
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, index=True, nullable=True)
    email = Column(String, index=True, nullable=True)
    address_lat = Column(Numeric(precision=9, scale=6), nullable=True)
    address_lon = Column(Numeric(precision=9, scale=6), nullable=True)
    address_description = Column(Text, nullable=True)
    bonus_balance = Column(Numeric(precision=10, scale=2), default=0.00)
    total_spent = Column(Numeric(precision=10, scale=2), default=0.00)
    order_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    referral_code = Column(String, unique=True, index=True, nullable=True)
    referred_by = Column(Integer, nullable=True)  # ID of the user who referred this user
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"