from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import math

from app.core.database import get_db
from app.core.config import settings
from app.schemas.delivery import (
    DeliveryZone, DeliveryZoneCreate, DeliveryZoneUpdate,
    DeliveryCost, DeliveryCostCreate, DeliveryCostUpdate,
    DeliveryCalculationRequest, DeliveryCalculationResponse,
    DeliverySettingsUpdate
)
from app.models.delivery import DeliveryZone as DeliveryZoneModel, DeliveryCost as DeliveryCostModel

router = APIRouter()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance = R * c
    return distance


def is_point_in_zone(lat: float, lon: float, zone: DeliveryZoneModel) -> bool:
    """Check if a point is within a delivery zone"""
    return (zone.min_lat <= lat <= zone.max_lat and 
            zone.min_lon <= lon <= zone.max_lon)


@router.get("/zones", response_model=List[DeliveryZone])
async def get_delivery_zones(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all delivery zones"""
    result = await db.execute(
        DeliveryZoneModel.__table__.select()
        .where(DeliveryZoneModel.is_active == True)
        .order_by(DeliveryZoneModel.id)
        .offset(skip)
        .limit(limit)
    )
    zones = result.fetchall()
    return [DeliveryZone.from_orm(row) for row in zones]


@router.get("/zones/{zone_id}", response_model=DeliveryZone)
async def get_delivery_zone(
    zone_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific delivery zone by ID"""
    result = await db.execute(
        DeliveryZoneModel.__table__.select()
        .where(DeliveryZoneModel.id == zone_id)
    )
    zone = result.fetchone()
    if not zone:
        raise HTTPException(status_code=404, detail="Delivery zone not found")
    return DeliveryZone.from_orm(zone)


@router.post("/zones", response_model=DeliveryZone)
async def create_delivery_zone(
    zone: DeliveryZoneCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new delivery zone"""
    db_zone = DeliveryZoneModel(**zone.dict())
    db.add(db_zone)
    await db.commit()
    await db.refresh(db_zone)
    return DeliveryZone.from_orm(db_zone)


@router.put("/zones/{zone_id}", response_model=DeliveryZone)
async def update_delivery_zone(
    zone_id: int,
    zone_update: DeliveryZoneUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a delivery zone"""
    result = await db.execute(
        DeliveryZoneModel.__table__.select()
        .where(DeliveryZoneModel.id == zone_id)
    )
    db_zone = result.fetchone()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Delivery zone not found")
    
    update_data = zone_update.dict(exclude_unset=True)
    await db.execute(
        DeliveryZoneModel.__table__.update()
        .where(DeliveryZoneModel.id == zone_id)
        .values(**update_data)
    )
    await db.commit()
    
    result = await db.execute(
        DeliveryZoneModel.__table__.select()
        .where(DeliveryZoneModel.id == zone_id)
    )
    updated_zone = result.fetchone()
    return DeliveryZone.from_orm(updated_zone)


@router.delete("/zones/{zone_id}")
async def delete_delivery_zone(
    zone_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a delivery zone (soft delete by setting is_active to False)"""
    result = await db.execute(
        DeliveryZoneModel.__table__.select()
        .where(DeliveryZoneModel.id == zone_id)
    )
    db_zone = result.fetchone()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Delivery zone not found")
    
    await db.execute(
        DeliveryZoneModel.__table__.update()
        .where(DeliveryZoneModel.id == zone_id)
        .values(is_active=False)
    )
    await db.commit()
    return {"message": "Delivery zone deleted successfully"}


@router.get("/costs", response_model=List[DeliveryCost])
async def get_delivery_costs(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all delivery costs"""
    result = await db.execute(
        DeliveryCostModel.__table__.select()
        .order_by(DeliveryCostModel.id)
        .offset(skip)
        .limit(limit)
    )
    costs = result.fetchall()
    return [DeliveryCost.from_orm(row) for row in costs]


@router.get("/costs/{cost_id}", response_model=DeliveryCost)
async def get_delivery_cost(
    cost_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific delivery cost by ID"""
    result = await db.execute(
        DeliveryCostModel.__table__.select()
        .where(DeliveryCostModel.id == cost_id)
    )
    cost = result.fetchone()
    if not cost:
        raise HTTPException(status_code=404, detail="Delivery cost not found")
    return DeliveryCost.from_orm(cost)


@router.post("/costs", response_model=DeliveryCost)
async def create_delivery_cost(
    cost: DeliveryCostCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new delivery cost"""
    db_cost = DeliveryCostModel(**cost.dict())
    db.add(db_cost)
    await db.commit()
    await db.refresh(db_cost)
    return DeliveryCost.from_orm(db_cost)


@router.put("/costs/{cost_id}", response_model=DeliveryCost)
async def update_delivery_cost(
    cost_id: int,
    cost_update: DeliveryCostUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a delivery cost"""
    result = await db.execute(
        DeliveryCostModel.__table__.select()
        .where(DeliveryCostModel.id == cost_id)
    )
    db_cost = result.fetchone()
    if not db_cost:
        raise HTTPException(status_code=404, detail="Delivery cost not found")
    
    update_data = cost_update.dict(exclude_unset=True)
    await db.execute(
        DeliveryCostModel.__table__.update()
        .where(DeliveryCostModel.id == cost_id)
        .values(**update_data)
    )
    await db.commit()
    
    result = await db.execute(
        DeliveryCostModel.__table__.select()
        .where(DeliveryCostModel.id == cost_id)
    )
    updated_cost = result.fetchone()
    return DeliveryCost.from_orm(updated_cost)


@router.post("/calculate", response_model=DeliveryCalculationResponse)
async def calculate_delivery(
    request: DeliveryCalculationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate delivery cost based on location and order amount"""
    # Get all active delivery zones
    zones_result = await db.execute(
        DeliveryZoneModel.__table__.select()
        .where(DeliveryZoneModel.is_active == True)
    )
    zones = zones_result.fetchall()
    
    # Find the zone for the given coordinates
    applicable_zone = None
    for zone in zones:
        if is_point_in_zone(request.lat, request.lon, zone):
            applicable_zone = zone
            break
    
    if not applicable_zone:
        return DeliveryCalculationResponse(
            delivery_cost=0,
            is_free=False,
            message="Delivery is not available to this location"
        )
    
    # Get delivery costs for this zone
    costs_result = await db.execute(
        DeliveryCostModel.__table__.select()
        .where(DeliveryCostModel.zone_id == applicable_zone.id)
        .order_by(DeliveryCostModel.min_order_amount.desc())
    )
    costs = costs_result.fetchall()
    
    # Find the applicable cost based on order amount
    applicable_cost = None
    for cost in costs:
        if request.order_amount >= cost.min_order_amount:
            applicable_cost = cost
            break
    
    # If no applicable cost found, use the one with the lowest min_order_amount
    if not applicable_cost and costs:
        applicable_cost = costs[-1]
    
    if not applicable_cost:
        # Calculate default cost based on distance
        distance = calculate_distance(
            settings.RESTAURANT_ADDRESS_LAT,
            settings.RESTAURANT_ADDRESS_LON,
            request.lat,
            request.lon
        )
        
        # Default calculation: base cost + cost per km
        delivery_cost = settings.DELIVERY_BASE_COST + (distance * settings.DELIVERY_COST_PER_KM)
        
        # Check if order amount qualifies for free delivery
        is_free = request.order_amount >= settings.FREE_DELIVERY_THRESHOLD
        final_cost = 0 if is_free else delivery_cost
        
        return DeliveryCalculationResponse(
            delivery_cost=round(final_cost, 2),
            is_free=is_free,
            zone_id=applicable_zone.id
        )
    
    # Use the configured delivery cost
    if applicable_cost.is_free:
        return DeliveryCalculationResponse(
            delivery_cost=0,
            is_free=True,
            zone_id=applicable_zone.id
        )
    
    if applicable_cost.is_flat_rate:
        # Check if order amount qualifies for free delivery
        is_free = request.order_amount >= settings.FREE_DELIVERY_THRESHOLD
        final_cost = 0 if is_free else applicable_cost.cost
        
        return DeliveryCalculationResponse(
            delivery_cost=round(final_cost, 2),
            is_free=is_free,
            zone_id=applicable_zone.id
        )
    
    # Calculate based on distance if not flat rate
    distance = calculate_distance(
        settings.RESTAURANT_ADDRESS_LAT,
        settings.RESTAURANT_ADDRESS_LON,
        request.lat,
        request.lon
    )
    
    delivery_cost = applicable_cost.cost + (distance * settings.DELIVERY_COST_PER_KM)
    is_free = request.order_amount >= settings.FREE_DELIVERY_THRESHOLD
    final_cost = 0 if is_free else delivery_cost
    
    return DeliveryCalculationResponse(
        delivery_cost=round(final_cost, 2),
        is_free=is_free,
        zone_id=applicable_zone.id
    )


@router.get("/settings")
async def get_delivery_settings():
    """Get current delivery settings"""
    return {
        "base_cost": settings.DELIVERY_BASE_COST,
        "cost_per_km": settings.DELIVERY_COST_PER_KM,
        "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
        "min_order_amount": settings.MIN_ORDER_AMOUNT,
        "restaurant_lat": settings.RESTAURANT_ADDRESS_LAT,
        "restaurant_lon": settings.RESTAURANT_ADDRESS_LON
    }


@router.put("/settings")
async def update_delivery_settings(settings_update: DeliverySettingsUpdate):
    """Update delivery settings"""
    # In a real implementation, this would update the settings in a database
    # For now, we just return the provided settings
    return settings_update