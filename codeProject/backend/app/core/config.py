import os
from typing import List, Optional
from pydantic import Field, validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL", "postgresql://user:password@localhost/restaurant_db"),
        description="PostgreSQL connection URL"
    )
    ASYNC_DATABASE_URL: str = Field(
        default=os.getenv("ASYNC_DATABASE_URL", "postgresql+asyncpg://user:password@localhost/restaurant_db"),
        description="PostgreSQL async connection URL"
    )

    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = Field(
        default=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        description="Token for Telegram Bot API"
    )
    TELEGRAM_WEBHOOK_URL: str = Field(
        default=os.getenv("TELEGRAM_WEBHOOK_URL", ""),
        description="Webhook URL for Telegram bot"
    )

    # Payment settings (Yookassa)
    YOOKASSA_SHOP_ID: str = Field(
        default=os.getenv("YOOKASSA_SHOP_ID", ""),
        description="Yookassa Shop ID"
    )
    YOOKASSA_API_KEY: str = Field(
        default=os.getenv("YOOKASSA_API_KEY", ""),
        description="Yookassa API Key"
    )
    YOOKASSA_WEBHOOK_URL: str = Field(
        default=os.getenv("YOOKASSA_WEBHOOK_URL", ""),
        description="Yookassa webhook URL"
    )

    # Application settings
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production"),
        min_length=32,
        description="Secret key for JWT encoding"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1, le=1440, description="Token expiration in minutes")

    # Delivery settings
    DELIVERY_BASE_COST: float = Field(default=200.0, ge=0, description="Base delivery cost in rubles")
    DELIVERY_COST_PER_KM: float = Field(default=25.0, ge=0, description="Delivery cost per kilometer")
    FREE_DELIVERY_THRESHOLD: float = Field(default=1500.0, ge=0, description="Order amount for free delivery")
    MIN_ORDER_AMOUNT: float = Field(default=500.0, ge=0, description="Minimum order amount")

    # Business settings
    RESTAURANT_ADDRESS_LAT: float = Field(
        default=float(os.getenv("RESTAURANT_ADDRESS_LAT", "55.7558")),
        ge=-90, le=90,
        description="Restaurant latitude (Moscow by default)"
    )
    RESTAURANT_ADDRESS_LON: float = Field(
        default=float(os.getenv("RESTAURANT_ADDRESS_LON", "37.6173")),
        ge=-180, le=180,
        description="Restaurant longitude (Moscow by default)"
    )

    # Notification settings
    SMS_API_KEY: Optional[str] = Field(
        default=os.getenv("SMS_API_KEY", None),
        description="SMS service API key"
    )
    SMS_SENDER_ID: Optional[str] = Field(
        default=os.getenv("SMS_SENDER_ID", None),
        description="Sender ID for SMS"
    )

    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "https://web.telegram.org",
            "https://t.me",
            "https://www.t.me",
            "https://telegram.org",
            "http://localhost:5173",
            "https://localhost:5173",
            "https://dev.proxy.example.com",
            "http://localhost:8000",
            "https://localhost:8000",
        ],
        description="Allowed CORS origins"
    )

    # Server settings (новые параметры)
    DEBUG: bool = Field(
        default=os.getenv("DEBUG", "False").lower() == "true",
        description="Debug mode"
    )
    HOST: str = Field(default=os.getenv("HOST", "0.0.0.0"), description="Server host")
    PORT: int = Field(default=int(os.getenv("PORT", 8000)), ge=1, le=65535, description="Server port")
    LOG_LEVEL: str = Field(
        default=os.getenv("LOG_LEVEL", "info"),
        description="Logging level"
    )

    # Application metadata
    APP_NAME: str = Field(default="Restaurant Telegram Mini App", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")

    # Валидаторы
    @field_validator("TELEGRAM_BOT_TOKEN")
    @classmethod
    def validate_telegram_token(cls, v: str) -> str:
        if v and not v.strip():
            raise ValueError("TELEGRAM_BOT_TOKEN cannot be empty if provided")
        return v.strip()

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if v == "your-secret-key-here-change-in-production":
            import warnings
            warnings.warn(
                "Using default SECRET_KEY! Change it in production!",
                UserWarning
            )
        return v

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def normalize_allowed_origins(cls, v: List[str]) -> List[str]:
        """Удаляем дубликаты и пустые строки"""
        return list(dict.fromkeys([origin.strip() for origin in v if origin.strip()]))

    # Проверка обязательных для продакшена полей
    def check_production_settings(self) -> None:
        """Проверяет настройки для продакшен окружения"""
        if not self.DEBUG:
            missing = []
            if not self.TELEGRAM_BOT_TOKEN:
                missing.append("TELEGRAM_BOT_TOKEN")
            if not self.YOOKASSA_SHOP_ID:
                missing.append("YOOKASSA_SHOP_ID")
            if not self.YOOKASSA_API_KEY:
                missing.append("YOOKASSA_API_KEY")

            if missing:
                raise ValueError(
                    f"Missing required production settings: {', '.join(missing)}"
                )

    # Свойства для удобства
    @property
    def database_config(self) -> dict:
        """Конфигурация базы данных"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": 10,
            "max_overflow": 20,
            "echo": self.DEBUG
        }

    @property
    def telegram_config(self) -> dict:
        """Конфигурация Telegram"""
        return {
            "bot_token": self.TELEGRAM_BOT_TOKEN,
            "webhook_url": self.TELEGRAM_WEBHOOK_URL,
        }

    @property
    def yookassa_config(self) -> dict:
        """Конфигурация Yookassa"""
        return {
            "shop_id": self.YOOKASSA_SHOP_ID,
            "api_key": self.YOOKASSA_API_KEY,
            "webhook_url": self.YOOKASSA_WEBHOOK_URL,
        }

    @property
    def delivery_config(self) -> dict:
        """Конфигурация доставки"""
        return {
            "base_cost": self.DELIVERY_BASE_COST,
            "cost_per_km": self.DELIVERY_COST_PER_KM,
            "free_threshold": self.FREE_DELIVERY_THRESHOLD,
            "min_order_amount": self.MIN_ORDER_AMOUNT,
            "restaurant_location": {
                "lat": self.RESTAURANT_ADDRESS_LAT,
                "lon": self.RESTAURANT_ADDRESS_LON
            }
        }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True
    )


# Создаем экземпляр настроек
settings = Settings()

# Проверяем настройки при импорте
if __name__ == "__main__":
    try:
        settings.check_production_settings()
        print("✅ Settings loaded successfully!")
        if settings.DEBUG:
            print(f"📝 Debug mode: ON")
            print(f"🌐 Allowed origins: {settings.ALLOWED_ORIGINS}")
    except Exception as e:
        print(f"❌ Error in settings: {e}")
        if settings.DEBUG:
            import traceback

            traceback.print_exc()