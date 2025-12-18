from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from ..database import metadata
from enum import Enum as PyEnum


class OrderStatus(str, PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order:
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_number = Column(String, unique=True, index=True, nullable=False)  # Generated order number
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    order_type = Column(String, nullable=False)  # "delivery" or "pickup"
    
    # Delivery information (nullable if order_type is "pickup")
    delivery_address_lat = Column(Numeric(precision=9, scale=6), nullable=True)
    delivery_address_lon = Column(Numeric(precision=9, scale=6), nullable=True)
    delivery_address_description = Column(Text, nullable=True)
    delivery_cost = Column(Numeric(precision=10, scale=2), default=0.00)
    delivery_time = Column(DateTime(timezone=True), nullable=True)
    
    # Pickup information (nullable if order_type is "delivery")
    pickup_time = Column(DateTime(timezone=True), nullable=True)
    
    # Payment information
    total_amount = Column(Numeric(precision=10, scale=2), nullable=False)
    bonus_used = Column(Numeric(precision=10, scale=2), default=0.00)  # Amount paid with bonuses
    final_amount = Column(Numeric(precision=10, scale=2), nullable=False)  # Total after bonuses
    payment_method = Column(String, nullable=False)  # "yookassa", "cash", etc.
    payment_status = Column(String, default="pending")  # "pending", "paid", "failed", "refunded"
    
    # Customer information
    customer_note = Column(Text, nullable=True)
    customer_phone = Column(String, nullable=True)  # In case different from user's phone
    
    # Internal notes
    admin_note = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class OrderItem:
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(precision=10, scale=2), nullable=False)  # Price at the time of order
    total_price = Column(Numeric(precision=10, scale=2), nullable=False)  # price * quantity
    note = Column(Text, nullable=True)  # Customer's note for this item
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class OrderStatusHistory:
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
    comment = Column(Text, nullable=True)  # Optional comment about the status change
    changed_by = Column(Integer, nullable=True)  # Admin user ID who changed the status
    created_at = Column(DateTime(timezone=True), server_default=func.now())