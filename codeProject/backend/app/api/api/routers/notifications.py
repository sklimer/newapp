from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ... import models, schemas

router = APIRouter()


@router.post("/notifications/send/", response_model=dict)
async def send_notification():
    # Implementation will go here
    pass