# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str

    # Hatchet Configuration (Optional)
    HATCHET_CLIENT_TOKEN: str
    HATCHET_SERVER_URL: str
    HATCHET_DEBUG: bool

    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    print(f"✅ Loaded config from: {settings.model_config['env_file']}")
    print(f"   ENVIRONMENT = {settings.ENVIRONMENT}")
    if settings.HATCHET_CLIENT_TOKEN:
        print("   Hatchet: Enabled")
    else:
        print("   Hatchet: Disabled (no token provided)")
    return settings


settings = get_settings()