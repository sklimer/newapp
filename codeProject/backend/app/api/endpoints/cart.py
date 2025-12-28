from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.users import User
from app.models.cart import CartItem
from app.models.menu import Product
from app.schemas.cart import CartItemResponse, CartItemCreate, CartItemUpdate
from app.schemas.users import UserResponse

router = APIRouter()


@router.post("/", response_model=CartItemResponse)
async def add_to_cart(
    cart_item: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверяем, существует ли продукт
    product_result = await db.execute(
        select(Product).where(Product.id == cart_item.product_id)
    )
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Проверяем, есть ли уже такой товар в корзине у пользователя
    existing_item_result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == current_user.id,
            CartItem.product_id == cart_item.product_id
        )
    )
    existing_item = existing_item_result.scalar_one_or_none()
    
    if existing_item:
        # Если товар уже есть в корзине, увеличиваем количество
        existing_item.quantity += cart_item.quantity
        await db.commit()
        await db.refresh(existing_item)
        return existing_item
    else:
        # Создаем новый элемент корзины
        db_cart_item = CartItem(
            user_id=current_user.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(db_cart_item)
        await db.commit()
        await db.refresh(db_cart_item)
        return db_cart_item


@router.get("/", response_model=List[CartItemResponse])
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == current_user.id)
    )
    cart_items = result.scalars().all()
    return cart_items


@router.put("/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: int,
    cart_item_update: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.user_id == current_user.id
        )
    )
    cart_item = result.scalar_one_or_none()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if cart_item_update.quantity is not None:
        if cart_item_update.quantity <= 0:
            # Если количество <= 0, удаляем элемент
            await db.delete(cart_item)
            await db.commit()
            raise HTTPException(status_code=200, detail="Cart item removed")
        else:
            cart_item.quantity = cart_item_update.quantity
    
    await db.commit()
    await db.refresh(cart_item)
    return cart_item


@router.delete("/{cart_item_id}")
async def remove_from_cart(
    cart_item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.user_id == current_user.id
        )
    )
    cart_item = result.scalar_one_or_none()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    await db.delete(cart_item)
    await db.commit()
    return {"detail": "Cart item removed successfully"}


@router.delete("/")
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await db.execute(
        CartItem.__table__.delete().where(CartItem.user_id == current_user.id)
    )
    await db.commit()
    return {"detail": "Cart cleared successfully"}