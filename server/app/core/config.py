from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    TESSERACT_PATH: str = "tesseract"
    GEMINI_API_KEY: str
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    
    REDIS_URL: str
    
    # Storage settings
    STORAGE: Literal["local", "cloud"] = "local"
    S3_BUCKET: str = "recipes-bucket"
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
