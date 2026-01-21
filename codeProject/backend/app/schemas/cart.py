# Добавьте это в ваш файл с схемами (вероятно, app/schemas/cart.py)
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Схема для продукта
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


# Ваши существующие схемы
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None


class CartItemBatchUpdate(BaseModel):
    product_id: int
    quantity: Optional[int] = None


# ОБНОВЛЕННАЯ схема - добавили поле product
class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductResponse] = None  # ДОБАВИЛИ ЭТО ПОЛЕ!

    class Config:
        from_attributes = True