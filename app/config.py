# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = Field(default="Hopemeals Guardian API")
    APP_ENV: str = Field(default="dev")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)

    # Mongo
    MONGO_URI: str = Field(default="mongodb://localhost:27017")
    MONGO_DB: str = Field(default="hopemeals_db")

    # Auth
    JWT_SECRET: str = Field(default="change_me_please")
    JWT_ALG: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=240)

    # OpenAI
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    OPENAI_TIMEOUT: int = Field(default=30)

settings = Settings()
