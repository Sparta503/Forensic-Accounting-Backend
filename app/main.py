# app/main.py
from dotenv import load_dotenv
from pathlib import Path

# Load .env manually
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from app.config.db import db

# Import your route modules here
from app.routes import auth, fraud  # <- THIS IS MISSING

app = FastAPI()

# Include your routes
app.include_router(auth.router)
app.include_router(fraud.router)