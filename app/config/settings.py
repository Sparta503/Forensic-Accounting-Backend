# app/config/settings.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
import sys

# Load .env safely (works in dev + PyInstaller)
_candidates: list[Path] = []

# 1) Next to the executable when packaged (or next to python.exe in dev)
try:
    _candidates.append(Path(sys.executable).resolve().parent / ".env")
except Exception:
    pass

# 2) Current working directory
_candidates.append(Path.cwd() / ".env")

# 3) Project patterns
_candidates.append(Path(__file__).resolve().parent.parent / ".env")
_candidates.append(Path(__file__).resolve().parent.parent.parent / ".env")

for _env_path in _candidates:
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path)
        break


class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    JWT_SECRET: str
    JWT_EXPIRES_HOURS: int = 2

    class Config:
        env_file = None
        case_sensitive = True


# Singleton instance
settings = Settings()