from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from enum import Enum


class DateRange(BaseModel):
    start_date: date
    end_date: date


class OrderAnalytics(BaseModel):
    total_orders: int
    total_revenue: float
    average_order_value: float
    total_items_sold: int
    date_range: DateRange


class UserAnalytics(BaseModel):
    total_users: int
    new_users: int
    active_users: int
    date_range: DateRange


class ProductAnalytics(BaseModel):
    product_id: int
    product_name: str
    total_sold: int
    total_revenue: float
    orders_count: int


class SalesReport(BaseModel):
    date: date
    total_orders: int
    total_revenue: float
    average_order_value: float


class AnalyticsResponse(BaseModel):
    orders: OrderAnalytics
    users: UserAnalytics
    top_products: list[ProductAnalytics]
    sales_trend: list[SalesReport]