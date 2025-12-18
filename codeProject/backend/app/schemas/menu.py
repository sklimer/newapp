from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    position: Optional[int] = 0
    is_active: bool = True
    is_stop_list: bool = False


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None
    is_stop_list: Optional[bool] = None


class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    discount_percent: Optional[int] = None
    weight: Optional[float] = None
    preparation_time: Optional[int] = None
    ingredients: Optional[str] = None
    position: Optional[int] = 0
    is_active: bool = True
    is_stop_list: bool = False
    is_recommended: bool = False
    is_new: bool = False


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    discount_percent: Optional[int] = None
    weight: Optional[float] = None
    preparation_time: Optional[int] = None
    ingredients: Optional[str] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None
    is_stop_list: Optional[bool] = None
    is_recommended: Optional[bool] = None
    is_new: Optional[bool] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductOptionBase(BaseModel):
    product_id: int
    name: str  # e.g., "Size", "Addition"
    type: str  # e.g., "single_choice", "multiple_choice"
    required: bool = False
    position: Optional[int] = 0
    is_active: bool = True


class ProductOptionCreate(ProductOptionBase):
    pass


class ProductOptionUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    required: Optional[bool] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None


class ProductOption(ProductOptionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductVariantBase(BaseModel):
    product_id: int
    option_id: Optional[int] = None  # Optional - for variants that don't belong to specific options
    name: str  # e.g., "Small", "Large", "Extra Cheese"
    price_addition: float = 0.00  # Additional cost
    position: Optional[int] = 0
    is_active: bool = True


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantUpdate(BaseModel):
    name: Optional[str] = None
    price_addition: Optional[float] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None


class ProductVariant(ProductVariantBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True