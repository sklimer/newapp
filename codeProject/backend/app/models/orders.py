from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.orm import declarative_base

from app.core.database import Base

class OrderStatus(str, enum.Enum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderType(str, enum.Enum):
    DELIVERY = "delivery"
    PICKUP = "pickup"


class Order(Base):
    __tablename__ = "orders"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_number: str = Column(String, unique=True, index=True, nullable=False)
    order_type: OrderType = Column(Enum(OrderType), nullable=False)
    status: OrderStatus = Column(Enum(OrderStatus), default=OrderStatus.CREATED)
    
    # Delivery information
    delivery_address_lat: Optional[Decimal] = Column(Numeric(precision=9, scale=6), nullable=True)
    delivery_address_lon: Optional[Decimal] = Column(Numeric(precision=9, scale=6), nullable=True)
    delivery_address_description: Optional[str] = Column(Text, nullable=True)
    delivery_distance: Optional[Decimal] = Column(Numeric(precision=8, scale=2), nullable=True)  # in km
    delivery_cost: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)
    
    # Pickup information
    pickup_time: Optional[datetime] = Column(DateTime, nullable=True)
    
    # Payment information
    subtotal: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # cost of items
    discount_amount: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)  # discount applied
    bonus_used: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)  # bonus rubles used
    total_amount: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # final amount
    paid_amount: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)  # amount actually paid
    payment_method: Optional[str] = Column(String, nullable=True)  # cash, card, yookassa, etc.
    payment_status: Optional[str] = Column(String, default="pending")  # pending, paid, failed, refunded
    
    # Customer information
    customer_note: Optional[str] = Column(Text, nullable=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    confirmed_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    delivered_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: int = Column(Integer, primary_key=True, index=True)
    order_id: int = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id: int = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity: int = Column(Integer, nullable=False)
    unit_price: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # price at time of order
    total_price: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # unit_price * quantity
    note: Optional[str] = Column(Text, nullable=True)  # customer's note for this item
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    options = relationship("OrderItemOption", back_populates="item")


class OrderItemOption(Base):
    __tablename__ = "order_item_options"

    id: int = Column(Integer, primary_key=True, index=True)
    order_item_id: int = Column(Integer, ForeignKey("order_items.id"), nullable=False)
    option_id: int = Column(Integer, ForeignKey("product_options.id"), nullable=False)
    name: str = Column(String, nullable=False)  # name of the option at time of order
    price_delta: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)  # price at time of order
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    item = relationship("OrderItem", back_populates="options")
    option = relationship("ProductOption", back_populates="selected_in_items")