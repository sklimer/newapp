from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeliveryZoneBase(BaseModel):
    name: str  # e.g., "Zone 1", "Downtown", etc.
    description: Optional[str] = None
    min_lat: float  # Minimum latitude of the zone
    max_lat: float  # Maximum latitude of the zone
    min_lon: float  # Minimum longitude of the zone
    max_lon: float  # Maximum longitude of the zone
    is_active: bool = True


class DeliveryZoneCreate(DeliveryZoneBase):
    pass


class DeliveryZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    min_lat: Optional[float] = None
    max_lat: Optional[float] = None
    min_lon: Optional[float] = None
    max_lon: Optional[float] = None
    is_active: Optional[bool] = None


class DeliveryZone(DeliveryZoneBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeliveryCostBase(BaseModel):
    zone_id: int
    min_order_amount: float = 0.00  # Minimum order for this delivery cost
    cost: float  # Delivery cost
    is_free: bool = False  # If True, delivery is free in this zone
    is_flat_rate: bool = False  # If True, cost is fixed regardless of distance


class DeliveryCostCreate(DeliveryCostBase):
    pass


class DeliveryCostUpdate(BaseModel):
    zone_id: Optional[int] = None
    min_order_amount: Optional[float] = None
    cost: Optional[float] = None
    is_free: Optional[bool] = None
    is_flat_rate: Optional[bool] = None


class DeliveryCost(DeliveryCostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeliveryCalculationRequest(BaseModel):
    lat: float
    lon: float
    order_amount: Optional[float] = 0.0


class DeliveryCalculationResponse(BaseModel):
    delivery_cost: float
    is_free: bool
    zone_id: Optional[int] = None
    message: Optional[str] = None


class DeliverySettingsBase(BaseModel):
    base_cost: float
    cost_per_km: float
    free_delivery_threshold: float
    min_order_amount: float
    restaurant_lat: float
    restaurant_lon: float


class DeliverySettingsUpdate(BaseModel):
    base_cost: Optional[float] = None
    cost_per_km: Optional[float] = None
    free_delivery_threshold: Optional[float] = None
    min_order_amount: Optional[float] = None
    restaurant_lat: Optional[float] = None
    restaurant_lon: Optional[float] = None