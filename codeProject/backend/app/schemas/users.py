from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address_lat: Optional[float] = None
    address_lon: Optional[float] = None
    address_description: Optional[str] = None
    bonus_balance: Optional[float] = 0.0
    referral_code: Optional[str] = None
    referred_by: Optional[int] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address_lat: Optional[float] = None
    address_lon: Optional[float] = None
    address_description: Optional[str] = None
    is_blocked: Optional[bool] = None


class User(UserBase):
    id: int
    total_spent: float
    order_count: int
    is_active: bool
    is_blocked: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True