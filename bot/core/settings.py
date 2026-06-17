from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BOT_DIR / "assets"

MEDIA_MAP = {
    "admin": ASSETS_DIR / "admin.jpg",
    "big_guarantor": ASSETS_DIR / "big_guarantor.png",
    "small_guarantor": ASSETS_DIR / "small_guarantor.jpg",
    "clean_user": ASSETS_DIR / "clean_user.png",
    "scammer": ASSETS_DIR / "scammer.png",
    "depositor": ASSETS_DIR / "depositor.png",
    "guarantor": ASSETS_DIR / "guarantor.png",
    "unknown_user": ASSETS_DIR / "unknown_user.png",
}


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    PROXY_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
