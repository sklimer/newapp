from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ... import models, schemas

router = APIRouter()


@router.get("/delivery/zones/", response_model=List[schemas.DeliveryZone])
async def get_delivery_zones(db: AsyncSession = Depends(get_db)):
    # Implementation will go here
    pass


@router.get("/delivery/calculate/", response_model=dict)
async def calculate_delivery_cost(
    lat: float,
    lon: float,
    order_amount: float = 0,
    db: AsyncSession = Depends(get_db)
):
    # Implementation will go here
    pass