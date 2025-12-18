from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float
    note: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    total_price: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    user_id: int
    order_type: str  # "delivery" or "pickup"
    total_amount: float
    bonus_used: Optional[float] = 0.0
    final_amount: float
    payment_method: str  # "yookassa", "cash", etc.
    customer_note: Optional[str] = None
    customer_phone: Optional[str] = None


class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate]
    # Delivery info (required if order_type is "delivery")
    delivery_address_lat: Optional[float] = None
    delivery_address_lon: Optional[float] = None
    delivery_address_description: Optional[str] = None
    delivery_time: Optional[datetime] = None
    # Pickup info (required if order_type is "pickup")
    pickup_time: Optional[datetime] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    delivery_address_lat: Optional[float] = None
    delivery_address_lon: Optional[float] = None
    delivery_address_description: Optional[str] = None
    delivery_time: Optional[datetime] = None
    pickup_time: Optional[datetime] = None
    admin_note: Optional[str] = None


class Order(OrderBase):
    id: int
    order_number: str
    status: OrderStatus
    delivery_cost: float
    payment_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrderItemSchema(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float
    total_price: float

    class Config:
        from_attributes = True

class OrderSchema(BaseModel):
    id: int
    user_id: int
    order_number: str
    status: str
    delivery_method: str
    payment_method: str
    total_amount: float
    discount_amount: float
    delivery_cost: float
    final_amount: float
    delivery_address: Optional[str]
    delivery_time: Optional[datetime]
    comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemSchema]

    class Config:
        from_attributes = True