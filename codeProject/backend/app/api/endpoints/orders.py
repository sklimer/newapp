from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from datetime import datetime

from app.core.database import get_db
from app.schemas.orders import Order, OrderCreate, OrderUpdate, OrderItem
from app.models.orders import Order as OrderModel, OrderItem as OrderItemModel
from app.models.users import User as UserModel
from app.models.menu import Product as ProductModel

router = APIRouter()


@router.get("/", response_model=List[Order])
async def get_orders(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    status: str = None
):
    """Get all orders with optional filters"""
    query = OrderModel.__table__.select()
    
    if user_id:
        query = query.where(OrderModel.user_id == user_id)
    if status:
        query = query.where(OrderModel.status == status)
    
    query = query.order_by(OrderModel.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    orders = result.fetchall()
    return [Order.from_orm(row) for row in orders]


@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific order by ID"""
    result = await db.execute(
        OrderModel.__table__.select()
        .where(OrderModel.id == order_id)
    )
    order = result.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order.from_orm(order)


@router.post("/", response_model=Order)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new order"""
    # Validate user exists
    user_result = await db.execute(
        UserModel.__table__.select()
        .where(UserModel.id == order.user_id)
    )
    user = user_result.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate unique order number
    order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    # Calculate total amount
    total_amount = order.total_amount
    final_amount = max(0, total_amount - order.bonus_used)
    
    # Create order
    order_data = order.dict()
    order_data["order_number"] = order_number
    order_data["final_amount"] = final_amount
    order_data["payment_status"] = "pending"
    
    db_order = OrderModel(**order_data)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    
    # Create order items
    for item in order.order_items:
        # Validate product exists
        product_result = await db.execute(
            ProductModel.__table__.select()
            .where(ProductModel.id == item.product_id)
        )
        product = product_result.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        # Calculate item total
        item_total = item.price * item.quantity
        
        order_item = OrderItemModel(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
            total_price=item_total,
            note=item.note
        )
        db.add(order_item)
    
    await db.commit()
    
    # Update user's order count and total spent
    await db.execute(
        UserModel.__table__.update()
        .where(UserModel.id == order.user_id)
        .values(
            order_count=UserModel.order_count + 1,
            total_spent=UserModel.total_spent + final_amount
        )
    )
    await db.commit()
    
    # If bonus was used, update user's bonus balance
    if order.bonus_used > 0:
        await db.execute(
            UserModel.__table__.update()
            .where(UserModel.id == order.user_id)
            .values(bonus_balance=UserModel.bonus_balance - order.bonus_used)
        )
        await db.commit()
    
    result = await db.execute(
        OrderModel.__table__.select()
        .where(OrderModel.id == db_order.id)
    )
    created_order = result.fetchone()
    return Order.from_orm(created_order)


@router.put("/{order_id}", response_model=Order)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an order"""
    result = await db.execute(
        OrderModel.__table__.select()
        .where(OrderModel.id == order_id)
    )
    db_order = result.fetchone()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_data = order_update.dict(exclude_unset=True)
    await db.execute(
        OrderModel.__table__.update()
        .where(OrderModel.id == order_id)
        .values(**update_data)
    )
    await db.commit()
    
    result = await db.execute(
        OrderModel.__table__.select()
        .where(OrderModel.id == order_id)
    )
    updated_order = result.fetchone()
    return Order.from_orm(updated_order)


@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an order (soft delete by setting is_active to False)"""
    result = await db.execute(
        OrderModel.__table__.select()
        .where(OrderModel.id == order_id)
    )
    db_order = result.fetchone()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    await db.execute(
        OrderModel.__table__.update()
        .where(OrderModel.id == order_id)
        .values(is_active=False)
    )
    await db.commit()
    return {"message": "Order deleted successfully"}


@router.get("/{order_id}/items", response_model=List[OrderItem])
async def get_order_items(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all items for an order"""
    result = await db.execute(
        OrderItemModel.__table__.select()
        .where(OrderItemModel.order_id == order_id)
    )
    items = result.fetchall()
    return [OrderItem.from_orm(row) for row in items]