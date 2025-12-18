import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/restaurant_db")
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    
    # Payment settings (Yookassa)
    YOOKASSA_SHOP_ID: str = os.getenv("YOOKASSA_SHOP_ID", "")
    YOOKASSA_API_KEY: str = os.getenv("YOOKASSA_API_KEY", "")
    YOOKASSA_WEBHOOK_URL: str = os.getenv("YOOKASSA_WEBHOOK_URL", "")
    
    # Application settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Delivery settings
    DELIVERY_BASE_COST: float = float(os.getenv("DELIVERY_BASE_COST", "200.0"))
    DELIVERY_COST_PER_KM: float = float(os.getenv("DELIVERY_COST_PER_KM", "25.0"))
    FREE_DELIVERY_THRESHOLD: float = float(os.getenv("FREE_DELIVERY_THRESHOLD", "1500.0"))
    MIN_ORDER_AMOUNT: float = float(os.getenv("MIN_ORDER_AMOUNT", "500.0"))
    
    # Business settings
    RESTAURANT_ADDRESS_LAT: float = float(os.getenv("RESTAURANT_ADDRESS_LAT", "0.0"))
    RESTAURANT_ADDRESS_LON: float = float(os.getenv("RESTAURANT_ADDRESS_LON", "0.0"))
    
    # Notification settings
    SMS_API_KEY: str = os.getenv("SMS_API_KEY", "")
    SMS_SENDER_ID: str = os.getenv("SMS_SENDER_ID", "")
    
    # CORS settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://your-frontend.vercel.app",
        "https://web.telegram.org",
        "https://t.me"
    ]

    class Config:
        env_file = ".env"


settings = Settings()