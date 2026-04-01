# app/config/settings.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
import os

# Resolve the absolute path to the .env file in the project root
env_path = Path(__file__).resolve().parent.parent / ".env"
print(f"Loading .env from: {env_path}")  # DEBUG
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    JWT_SECRET: str

    class Config:
        env_file = None  # disable Pydantic's automatic .env search
        case_sensitive = True

# Debug: check if env is loaded
print("MONGO_URI from os.environ:", os.getenv("MONGO_URI"))

settings = Settings()