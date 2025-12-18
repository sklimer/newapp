from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    ORDER_STATUS = "order_status"
    PROMOTION = "promotion"
    SYSTEM = "system"


class NotificationChannel(str, Enum):
    TELEGRAM = "telegram"
    SMS = "sms"
    EMAIL = "email"


class NotificationBase(BaseModel):
    user_id: int
    title: str
    message: str
    type: NotificationType
    is_read: bool = False
    channel: NotificationChannel


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class Notification(NotificationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationRequest(BaseModel):
    user_id: int
    title: str
    message: str
    type: NotificationType
    channel: NotificationChannel


class NotificationResponse(BaseModel):
    success: bool
    message: str
    notification_id: Optional[int] = None