from fastapi import APIRouter
from app.api.endpoints import (
    admin,
    analytics,
    auth,
    bonus,
    business,
    cart,
    delivery,
    menu,
    notification,
    orders,
    payments,
    profile,
    telegram_auth,
    users
)
from app.api.api_docs import router as docs_router

api_router = APIRouter()

# Подключаем маршруты с новыми префиксами для v2
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(menu.router, prefix="/menu", tags=["menu"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(delivery.router, prefix="/delivery", tags=["delivery"])
api_router.include_router(bonus.router, prefix="/bonus", tags=["bonus"])
api_router.include_router(notification.router, prefix="/notification", tags=["notification"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(business.router, prefix="/business", tags=["business"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(telegram_auth.router, prefix="/telegram", tags=["telegram_auth"])
api_router.include_router(docs_router, prefix="/docs", tags=["documentation"])