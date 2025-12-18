from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BonusProgramBase(BaseModel):
    name: str  # e.g., "Registration Bonus", "Order Bonus"
    description: Optional[str] = None
    type: str  # "registration", "order_percent", "fixed_amount", "referral"
    value: float  # Bonus amount or percentage
    min_order_amount: Optional[float] = None  # Minimum order to earn bonus
    max_bonus_amount: Optional[float] = None  # Max bonus for percentage-based
    is_active: bool = True
    is_default: bool = False  # If True, this is the default bonus program


class BonusProgramCreate(BonusProgramBase):
    pass


class BonusProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    value: Optional[float] = None
    min_order_amount: Optional[float] = None
    max_bonus_amount: Optional[float] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class BonusProgram(BonusProgramBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BonusTransactionBase(BaseModel):
    user_id: int
    program_id: int
    order_id: Optional[int] = None  # Nullable for registration bonuses
    amount: float  # Positive for earned, negative for used
    balance_before: float
    balance_after: float
    description: Optional[str] = None
    transaction_type: str  # "earned", "used", "referral_bonus"


class BonusTransactionCreate(BonusTransactionBase):
    pass


class BonusTransaction(BonusTransactionBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ApplyBonusRequest(BaseModel):
    user_id: int
    bonus_amount: float


class BonusBalanceResponse(BaseModel):
    user_id: int
    bonus_balance: float