import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api.deps import get_db, get_admin_user
from app.core.security import create_access_token
from app.models.users import User as UserModel

router = APIRouter()
logger = logging.getLogger(__name__)


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Simple example implementation - you would add proper authentication logic here
    # For now, using a basic approach to validate user
    from sqlalchemy import select
    
    query = select(UserModel).where(UserModel.username == request.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or request.password != "temp_password":  # Replace with proper password checking
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=30)  # Set appropriate expiration
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/admin-test")
async def admin_test(current_user = Depends(get_admin_user)):
    """
    Test endpoint to verify admin access
    """
    return {"message": "Admin access verified", "user_id": current_user.id}