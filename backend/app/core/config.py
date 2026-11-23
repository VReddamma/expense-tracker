from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application settings
    APP_NAME: str = "Expense Tracker API"
    DATABASE_URL: str
    DEBUG: bool = False

    # JWT settings
    SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: Literal["HS256"] = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)

    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
