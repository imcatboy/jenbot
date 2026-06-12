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
    ALLOWED_AVATAR_EXTENSIONS: List[str]
    AVATAR_MAX_SIZE: int
    AVATAR_SIZE: List[int]
    ALLOWED_PRODUCT_IMAGE_EXTENSIONS: List[str]
    PRODUCT_IMAGE_MAX_SIZE: int
    PRODUCT_IMAGE_SIZE: List[int]
    ALLOWED_MESSAGE_FILE_EXTENSIONS: List[str]
    MESSAGE_FILE_MAX_SIZE: int
    AVATAR_STORAGE_PATH: str
    PRODUCT_IMAGE_STORAGE_PATH: str
    MESSAGE_FILE_STORAGE_PATH: str
    FILE_MAX_NAME_LENGTH: int
    SENTRY_DSN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
