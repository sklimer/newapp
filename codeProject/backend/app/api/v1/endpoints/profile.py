from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.models.users import User
from app.schemas.users import UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current user profile
    """
    return UserResponse.from_orm(current_user)


@router.put("/", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update current user profile
    """
    update_data = user_update.dict(exclude_unset=True)
    
    # Update user fields
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)