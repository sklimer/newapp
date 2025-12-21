from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

from app.core.database import Base


class Business(Base):
    __tablename__ = "businesses"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False)  # restaurant name
    description: Optional[str] = Column(Text, nullable=True)
    phone_number: str = Column(String, nullable=False)
    email: Optional[str] = Column(String, nullable=True)
    website: Optional[str] = Column(String, nullable=True)
    address: str = Column(String, nullable=False)
    address_lat: Decimal = Column(Numeric(precision=9, scale=6), nullable=False)
    address_lon: Decimal = Column(Numeric(precision=9, scale=6), nullable=False)
    working_hours: Optional[str] = Column(Text, nullable=True)  # e.g., "Mon-Fri: 10:00-22:00"
    is_active: bool = Column(Boolean, default=True)
    logo_url: Optional[str] = Column(String, nullable=True)
    cover_image_url: Optional[str] = Column(String, nullable=True)
    
    # Business settings
    min_order_amount: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)
    free_delivery_threshold: Decimal = Column(Numeric(precision=10, scale=2), default=1000.00)
    delivery_cost_per_km: Decimal = Column(Numeric(precision=10, scale=2), default=50.00)
    base_delivery_cost: Decimal = Column(Numeric(precision=10, scale=2), default=200.00)
    max_delivery_distance: Decimal = Column(Numeric(precision=8, scale=2), default=20.00)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class BusinessAdmin(Base):
    __tablename__ = "business_admins"

    id: int = Column(Integer, primary_key=True, index=True)
    business_id: int = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    role: str = Column(String, default="admin")  # admin, manager, staff
    is_active: bool = Column(Boolean, default=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    business = relationship("Business")
    user = relationship("User")


class BusinessHours(Base):
    __tablename__ = "business_hours"

    id: int = Column(Integer, primary_key=True, index=True)
    business_id: int = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    day_of_week: int = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    open_time: str = Column(String, nullable=False)  # e.g., "09:00"
    close_time: str = Column(String, nullable=False)  # e.g., "21:00"
    is_closed: bool = Column(Boolean, default=False)  # whether the business is closed on this day
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    business = relationship("Business")


class BusinessImage(Base):
    __tablename__ = "business_images"

    id: int = Column(Integer, primary_key=True, index=True)
    business_id: int = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    image_url: str = Column(String, nullable=False)
    alt_text: Optional[str] = Column(String, nullable=True)
    is_primary: bool = Column(Boolean, default=False)  # whether this is the main image
    position: int = Column(Integer, default=0)  # for ordering
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    business = relationship("Business")