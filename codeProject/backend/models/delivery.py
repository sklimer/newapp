from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import metadata


class DeliveryZone:
    __tablename__ = "delivery_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Zone 1", "Downtown", etc.
    description = Column(Text, nullable=True)
    min_lat = Column(Numeric(precision=9, scale=6), nullable=False)  # Minimum latitude of the zone
    max_lat = Column(Numeric(precision=9, scale=6), nullable=False)  # Maximum latitude of the zone
    min_lon = Column(Numeric(precision=9, scale=6), nullable=False)  # Minimum longitude of the zone
    max_lon = Column(Numeric(precision=9, scale=6), nullable=False)  # Maximum longitude of the zone
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class DeliveryCost:
    __tablename__ = "delivery_costs"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("delivery_zones.id"), nullable=False)
    min_order_amount = Column(Numeric(precision=10, scale=2), default=0.00)  # Minimum order for this delivery cost
    cost = Column(Numeric(precision=10, scale=2), nullable=False)  # Delivery cost
    is_free = Column(Boolean, default=False)  # If True, delivery is free in this zone
    is_flat_rate = Column(Boolean, default=False)  # If True, cost is fixed regardless of distance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())