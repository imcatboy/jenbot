from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE: int
    REFRESH_TOKEN_EXPIRE: int
    DATABASE_URL: str
    SECRET_KEY: str
    CORS_ALLOW_ORIGINS: List[str]
    CORS_ALLOW_HEADERS: List[str]
    ALGORITHM: str

    model_config = SettingsConfigDict(env_file=".env")