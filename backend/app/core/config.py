from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://aixp:aixp_secure_2024@postgres:5432/aixp"

    # Redis
    redis_url: str = "redis://:aixp_redis_2024@redis:6379/0"

    # Celery
    celery_broker_url: str = "redis://:aixp_redis_2024@redis:6379/1"
    celery_result_backend: str = "redis://:aixp_redis_2024@redis:6379/2"

    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "aixpadmin"
    minio_secret_key: str = "aixp_minio_2024"
    minio_bucket: str = "aixp-files"
    minio_secure: bool = False

    # AI
    ollama_host: str = "http://ollama:11434"
    default_ai_model: str = "llama3.1:8b"
    fallback_ai_provider: str = ""
    openai_api_key: str = ""

    # Security
    secret_key: str = "aixp_secret_key_change_me"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # App
    environment: str = "production"
    app_name: str = "AI-XP"
    app_url: str = "https://localhost"

    # Connectors
    whatsapp_api_key: str = ""
    telegram_bot_token: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_tls: bool = True

    # Meta / Facebook Messenger
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_verify_token: str = ""
    meta_page_access_token: str = ""

    # WordPress
    wp_webhook_secret: str = "wp_webhook_secret_2024"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
