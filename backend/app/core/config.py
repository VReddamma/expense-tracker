from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Expense Tracker API"
    DATABASE_URL: str
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
