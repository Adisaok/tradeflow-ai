from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TradeFlow AI"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://tradeflow:tradeflow_dev_password@localhost:5432/tradeflow"
    redis_url: str = "redis://localhost:6379/0"
    blaaiz_env: str = "development"
    blaaiz_api_url: str = "https://api-dev.blaaiz.com"
    blaaiz_client_id: str = ""
    blaaiz_client_secret: str = ""
    blaaiz_oauth_scope: str = "wallet:read currency:read rates:read fees:read payout:create transaction:read"
    blaaiz_webhook_secret: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
