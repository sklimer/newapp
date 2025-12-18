from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class NotificationType(str, enum.Enum):
    ORDER_STATUS = "order_status"
    PROMOTION = "promotion"
    BONUS = "bonus"
    SYSTEM = "system"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class NotificationChannel(str, enum.Enum):
    TELEGRAM = "telegram"
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"


class Notification(Base):
    __tablename__ = "notifications"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    type: NotificationType = Column(Enum(NotificationType), nullable=False)
    status: NotificationStatus = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    channel: NotificationChannel = Column(Enum(NotificationChannel), nullable=False)
    
    title: str = Column(String, nullable=False)
    message: str = Column(Text, nullable=False)
    data: Optional[dict] = Column(Text, nullable=True)  # Additional data for the notification
    
    # Delivery information
    sent_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    read_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")