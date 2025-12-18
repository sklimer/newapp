from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import hashlib
import hmac
import time

from app.core.database import get_db
from app.core.config import settings
from app.schemas.users import User, UserCreate, UserUpdate
from app.models.users import User as UserModel
from app.schemas.orders import OrderSchema
router = APIRouter()


def verify_telegram_auth(auth_data: dict):
    """Verify Telegram authentication data"""
    # Create a string for data check
    data_check_arr = []
    for key, value in auth_data.items():
        if key != 'hash':
            data_check_arr.append(f"{key}={value}")
    
    data_check_arr.sort()
    data_check_string = '\n'.join(data_check_arr)
    
    # Create secret key
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    
    # Create hash
    hash_calculated = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    # Compare hashes
    return hmac.compare_digest(hash_calculated, auth_data['hash'])


@router.get("/", response_model=List[User])
async def get_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all users"""
    result = await db.execute(
        UserModel.__table__.select()
        .order_by(UserModel.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    users = result.fetchall()
    return [User.from_orm(row) for row in users]


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user by ID"""
    result = await db.execute(
        UserModel.__table__.select()
        .where(UserModel.id == user_id)
    )
    user = result.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User.from_orm(user)


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    # Check if user already exists by telegram_id
    result = await db.execute(
        UserModel.__table__.select()
        .where(UserModel.telegram_id == user.telegram_id)
    )
    existing_user = result.fetchone()
    if existing_user:
        # If user already exists, return the existing user
        return User.from_orm(existing_user)
    
    # Generate referral code if not provided
    if not user.referral_code:
        import secrets
        user.referral_code = f"REF{secrets.token_urlsafe(8).upper()[:8]}"
    
    db_user = UserModel(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return User.from_orm(db_user)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a user"""
    result = await db.execute(
        UserModel.__table__.select()
        .where(UserModel.id == user_id)
    )
    db_user = result.fetchone()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    await db.execute(
        UserModel.__table__.update()
        .where(UserModel.id == user_id)
        .values(**update_data)
    )
    await db.commit()
    
    result = await db.execute(
        UserModel.__table__.select()
        .where(UserModel.id == user_id)
    )
    updated_user = result.fetchone()
    return User.from_orm(updated_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a user (soft delete by setting is_active to False)"""
    result = await db.execute(
        UserModel.__table__.select()
        .where(UserModel.id == user_id)
    )
    db_user = result.fetchone()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.execute(
        UserModel.__table__.update()
        .where(UserModel.id == user_id)
        .values(is_active=False)
    )
    await db.commit()
    return {"message": "User deleted successfully"}


@router.post("/telegram-auth")
async def telegram_auth(
    auth_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user via Telegram"""
    # Verify the authentication data
    if not verify_telegram_auth(auth_data):
        raise HTTPException(status_code=400, detail="Invalid authentication data")
    
    # Check if user already exists
    result = await db.execute(
        UserModel.__table__.select()
        .where(UserModel.telegram_id == str(auth_data['id']))
    )
    user = result.fetchone()
    
    if user:
        # Update user data if changed
        update_data = {
            'first_name': auth_data.get('first_name'),
            'last_name': auth_data.get('last_name'),
            'username': auth_data.get('username'),
        }
        await db.execute(
            UserModel.__table__.update()
            .where(UserModel.id == user.id)
            .values(**update_data)
        )
        await db.commit()
        return User.from_orm(user)
    else:
        # Create new user
        user_data = {
            'telegram_id': str(auth_data['id']),
            'first_name': auth_data.get('first_name'),
            'last_name': auth_data.get('last_name'),
            'username': auth_data.get('username'),
            'referral_code': f"REF{str(auth_data['id'])[-6:].upper()}"  # Generate referral code
        }
        
        db_user = UserModel(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return User.from_orm(db_user)


@router.get("/{user_id}/orders", response_model=List[OrderSchema])
async def get_user_orders(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a specific user"""
    from app.models.orders import Order as OrderModel
    from app.schemas.orders import Order as OrderSchema
    
    result = await db.execute(
        OrderModel.__table__.select()
        .where(OrderModel.user_id == user_id)
        .order_by(OrderModel.created_at.desc())
    )
    orders = result.fetchall()
    return [OrderSchema.from_orm(row) for row in orders]