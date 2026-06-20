from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str
    debug: bool
    base_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    database_url: str
    redis_url: str
    rate_limit_create_url: int
    rate_limit_click_url: int
    rate_limit_window_seconds: int
    short_code_length: int
    allowed_origins: str  # ← Changed from List[str] to str
    admin_email: str
    admin_password: str
    admin_username: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()