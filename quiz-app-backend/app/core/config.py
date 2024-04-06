# filename: app/core/config.py
from pydantic_settings import BaseSettings

class SettingsCore(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"

settings_core = SettingsCore()
