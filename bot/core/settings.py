from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    PROXY_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


MEDIA_MAP = {
    "admin": "assets/admin.jpg",
    "big_guarantor": "assets/big_guarantor.png",
    "small_guarantor": "assets/small_guarantor.jpg",
    "user": "assets/user.png",
    "scammer": "assets/scammer.png",
    "depositor": "assets/depositor.png",
    "guarantor": "assets/guarantor.png",
}
