from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    CORS_ALLOW_ORIGINS: List[str]
    CORS_ALLOW_HEADERS: List[str]
    PROJECT_HOST: str
    PROJECT_PORT: int
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    model_config = SettingsConfigDict(env_file=".env")