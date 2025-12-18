from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    image_url: Optional[str] = Column(String, nullable=True)
    position: int = Column(Integer, default=0)
    is_active: bool = Column(Boolean, default=True)
    is_stop_list: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationship
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: int = Column(Integer, primary_key=True, index=True)
    category_id: int = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name: str = Column(String, nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    image_url: Optional[str] = Column(String, nullable=True)
    price: Decimal = Column(Numeric(precision=10, scale=2), nullable=False)
    discount_price: Optional[Decimal] = Column(Numeric(precision=10, scale=2), nullable=True)
    discount_percent: Optional[int] = Column(Integer, nullable=True)
    weight: Optional[Decimal] = Column(Numeric(precision=10, scale=3), nullable=True)
    preparation_time: Optional[int] = Column(Integer, nullable=True)  # in minutes
    ingredients: Optional[str] = Column(Text, nullable=True)
    position: int = Column(Integer, default=0)
    is_active: bool = Column(Boolean, default=True)
    is_stop_list: bool = Column(Boolean, default=False)
    is_recommended: bool = Column(Boolean, default=False)
    is_new: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    variants = relationship("ProductVariant", back_populates="product")
    option_groups = relationship("ProductOptionGroup", back_populates="product")


class ProductCategory(Base):
    __tablename__ = 'product_categories'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)


class ProductOptionGroup(Base):
    __tablename__ = "product_option_groups"

    id: int = Column(Integer, primary_key=True, index=True)
    product_id: int = Column(Integer, ForeignKey("products.id"), nullable=False)
    name: str = Column(String, nullable=False)  # e.g., "Size", "Topping", "Sauce"
    min_selections: int = Column(Integer, default=0)  # minimum number of options to select
    max_selections: int = Column(Integer, default=1)  # maximum number of options to select
    is_required: bool = Column(Boolean, default=False)
    position: int = Column(Integer, default=0)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="option_groups")
    options = relationship("ProductOption", back_populates="group")


class ProductOption(Base):
    __tablename__ = "product_options"

    id: int = Column(Integer, primary_key=True, index=True)
    group_id: int = Column(Integer, ForeignKey("product_option_groups.id"), nullable=False)
    name: str = Column(String, nullable=False)  # e.g., "Small", "Large", "Extra Cheese"
    price_delta: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)  # additional cost
    is_available: bool = Column(Boolean, default=True)
    position: int = Column(Integer, default=0)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    group = relationship("ProductOptionGroup", back_populates="options")
    selected_in_items = relationship("OrderItemOption", back_populates="option")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: int = Column(Integer, primary_key=True, index=True)
    product_id: int = Column(Integer, ForeignKey("products.id"), nullable=False)
    option_id: Optional[int] = Column(Integer, ForeignKey("product_options.id"), nullable=True)  # Optional - for variants that don't belong to specific options
    name: str = Column(String, nullable=False)  # e.g., "Small", "Large", "Extra Cheese"
    price_addition: Decimal = Column(Numeric(precision=10, scale=2), default=0.00)  # Additional cost
    position: int = Column(Integer, default=0)
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="variants")
    option = relationship("ProductOption")