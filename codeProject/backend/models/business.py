from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import metadata


class Restaurant:
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=False)
    address_lat = Column(Numeric(precision=9, scale=6), nullable=False)
    address_lon = Column(Numeric(precision=9, scale=6), nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    working_hours = Column(Text, nullable=True)  # JSON string or text
    min_order_amount = Column(Numeric(precision=10, scale=2), default=500.00)
    free_delivery_threshold = Column(Numeric(precision=10, scale=2), default=1500.00)
    delivery_base_cost = Column(Numeric(precision=10, scale=2), default=200.00)
    delivery_cost_per_km = Column(Numeric(precision=10, scale=2), default=25.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class AdminUser:
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(String, default="admin")  # "admin", "manager", "operator"
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())