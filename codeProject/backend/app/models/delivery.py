from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DeliveryZone(Base):
    __tablename__ = "delivery_zones"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False)  # e.g., "Zone 1", "Downtown"
    description: Optional[str] = Column(Text, nullable=True)
    min_order_amount: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)  # minimum order amount for this zone
    base_cost: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # base delivery cost
    cost_per_km: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # cost per kilometer
    is_active: bool = Column(Boolean, default=True)
    
    # Zone boundaries (for more advanced zone-based delivery)
    center_lat: Decimal = Column(Numeric(precision=9, scale=6), nullable=False)  # center latitude
    center_lon: Decimal = Column(Numeric(precision=9, scale=6), nullable=False)  # center longitude
    radius_km: Decimal = Column(Numeric(precision=8, scale=2), nullable=False)  # radius in km
    min_lat: Decimal = Column(Numeric(precision=9, scale=6), nullable=False)  # minimum latitude
    max_lat: Decimal = Column(Numeric(precision=9, scale=6), nullable=False)  # maximum latitude
    min_lon: Decimal = Column(Numeric(precision=9, scale=6), nullable=False)  # minimum longitude
    max_lon: Decimal = Column(Numeric(precision=9, scale=6), nullable=False)  # maximum longitude
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class DeliveryCost(Base):
    __tablename__ = "delivery_costs"

    id: int = Column(Integer, primary_key=True, index=True)
    zone_id: int = Column(Integer, ForeignKey("delivery_zones.id"), nullable=False)  # reference to delivery zone
    min_order_amount: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)  # minimum order amount for this delivery cost
    cost: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # delivery cost
    is_free: bool = Column(Boolean, default=False)  # if True, delivery is free in this zone
    is_flat_rate: bool = Column(Boolean, default=False)  # if True, cost is fixed regardless of distance
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    zone = relationship("DeliveryZone")


class DeliverySettings(Base):
    __tablename__ = "delivery_settings"

    id: int = Column(Integer, primary_key=True, index=True)
    restaurant_lat: Decimal = Column(Numeric(precision=9, scale=6), nullable=False)  # restaurant latitude
    restaurant_lon: Decimal = Column(Numeric(precision=9, scale=6), nullable=False)  # restaurant longitude
    default_zone_id: int = Column(Integer, ForeignKey("delivery_zones.id"), nullable=False)  # default delivery zone
    free_delivery_threshold: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # order amount for free delivery
    min_order_amount: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # minimum order amount
    max_delivery_distance: Decimal = Column(Numeric(precision=8, scale=2), nullable=False)  # maximum delivery distance in km
    delivery_time_estimate: int = Column(Integer, nullable=False)  # estimated delivery time in minutes
    is_active: bool = Column(Boolean, default=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    default_zone = relationship("DeliveryZone")


class DeliveryPerson(Base):
    __tablename__ = "delivery_persons"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=True)  # link to user if applicable
    first_name: str = Column(String, nullable=False)
    last_name: str = Column(String, nullable=False)
    phone_number: str = Column(String, nullable=False)
    vehicle_type: str = Column(String, default="bike")  # bike, car, motorcycle
    license_plate: Optional[str] = Column(String, nullable=True)
    is_active: bool = Column(Boolean, default=True)
    current_lat: Optional[Decimal] = Column(Numeric(precision=9, scale=6), nullable=True)  # current location
    current_lon: Optional[Decimal] = Column(Numeric(precision=9, scale=6), nullable=True)  # current location
    is_available: bool = Column(Boolean, default=True)  # whether person is available for delivery
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User")


class DeliveryDistance(Base):
    __tablename__ = 'delivery_distances'

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, nullable=False)
    distance = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(String(1), default='Y')