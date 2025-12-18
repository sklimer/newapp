from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import metadata


class Category:
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    position = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_stop_list = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Product:
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    price = Column(Numeric(precision=10, scale=2), nullable=False)
    discount_price = Column(Numeric(precision=10, scale=2), nullable=True)  # Price with discount
    discount_percent = Column(Integer, nullable=True)  # Discount percentage
    weight = Column(Numeric(precision=8, scale=2), nullable=True)  # Weight in grams
    preparation_time = Column(Integer, nullable=True)  # Preparation time in minutes
    ingredients = Column(Text, nullable=True)  # JSON string or text
    position = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_stop_list = Column(Boolean, default=False)  # For when ingredients are unavailable
    is_recommended = Column(Boolean, default=False)
    is_new = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class ProductOption:
    __tablename__ = "product_options"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "Size", "Addition"
    type = Column(String, nullable=False)  # e.g., "single_choice", "multiple_choice"
    required = Column(Boolean, default=False)
    position = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class ProductVariant:
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    option_id = Column(Integer, ForeignKey("product_options.id"), nullable=True)  # Optional - for variants that don't belong to specific options
    name = Column(String, nullable=False)  # e.g., "Small", "Large", "Extra Cheese"
    price_addition = Column(Numeric(precision=10, scale=2), default=0.00)  # Additional cost
    is_active = Column(Boolean, default=True)
    position = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())