from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ... import models, schemas

router = APIRouter()


@router.get("/users/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass


@router.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass


@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass


@router.get("/users/", response_model=List[schemas.User])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass