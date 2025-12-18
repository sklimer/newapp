from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import metadata


class NotificationTemplate:
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "order_confirmed", "delivery_eta"
    title = Column(String, nullable=True)  # Notification title
    message = Column(Text, nullable=False)  # Notification message with placeholders
    type = Column(String, nullable=False)  # "order_status", "promotional", "system"
    channel = Column(String, nullable=False)  # "telegram", "sms", "email", "push"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Notification:
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("notification_templates.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # Nullable for non-order notifications
    title = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    channel = Column(String, nullable=False)  # "telegram", "sms", "email", "push"
    status = Column(String, default="pending")  # "pending", "sent", "failed"
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())