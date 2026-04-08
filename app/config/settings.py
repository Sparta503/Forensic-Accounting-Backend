# app/config/settings.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

# Load .env safely
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    JWT_SECRET: str

    class Config:
        env_file = None
        case_sensitive = True


# Singleton instance
settings = Settings()