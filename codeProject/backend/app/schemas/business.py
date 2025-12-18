from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time


class BusinessSettingsBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    phone: str
    email: Optional[str] = None
    working_hours_start: time
    working_hours_end: time
    min_order_amount: Optional[float] = 0.0
    free_delivery_threshold: Optional[float] = 0.0
    delivery_cost: Optional[float] = 0.0
    delivery_cost_per_km: Optional[float] = 0.0
    is_active: bool = True


class BusinessSettingsCreate(BusinessSettingsBase):
    pass


class BusinessSettingsUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    working_hours_start: Optional[time] = None
    working_hours_end: Optional[time] = None
    min_order_amount: Optional[float] = None
    free_delivery_threshold: Optional[float] = None
    delivery_cost: Optional[float] = None
    delivery_cost_per_km: Optional[float] = None
    is_active: Optional[bool] = None


class BusinessSettings(BusinessSettingsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BusinessHoursBase(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    is_open: bool
    open_time: Optional[time] = None
    close_time: Optional[time] = None


class BusinessHoursCreate(BusinessHoursBase):
    pass


class BusinessHoursUpdate(BaseModel):
    is_open: Optional[bool] = None
    open_time: Optional[time] = None
    close_time: Optional[time] = None


class BusinessHours(BusinessHoursBase):
    id: int
    business_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True