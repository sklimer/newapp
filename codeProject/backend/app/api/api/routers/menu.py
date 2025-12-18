from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ... import models, schemas

router = APIRouter()


@router.get("/categories/", response_model=List[schemas.Category])
async def get_categories(db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass


@router.post("/categories/", response_model=schemas.Category)
async def create_category(category: schemas.CategoryCreate, db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass


@router.get("/products/", response_model=List[schemas.Product])
async def get_products(db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass


@router.post("/products/", response_model=schemas.Product)
async def create_product(product: schemas.ProductCreate, db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass