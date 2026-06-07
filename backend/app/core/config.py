from pydantic_settings import BaseSettings
from typing import List
import secrets


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MedInsure API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://medinsure:password@localhost:5432/medinsure_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://medinsure.vercel.app",
    ]

    # ML
    ML_MODELS_PATH: str = "app/ml/models"
    ML_DATA_PATH: str = "app/ml/data"
    MODEL_RETRAIN_THRESHOLD: int = 1000  # retrain after N new samples

    # PDF
    PDF_OUTPUT_PATH: str = "/tmp/reports"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
