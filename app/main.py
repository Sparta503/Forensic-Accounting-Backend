# app/main.py
from dotenv import load_dotenv
from pathlib import Path
from app.routes import reports
from app.routes import analysis

# -------------------------------
# Load .env manually (SAFE)
# -------------------------------
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config.settings import settings

# Import routes
from app.routes import auth, fraud, transactions, financial


# -------------------------------
# App Lifecycle (Startup / Shutdown)
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    print(f"✅ Connected to {settings.DB_NAME} Database")

    yield

    # SHUTDOWN
    print("🛑 Application shutting down...")


# -------------------------------
# Initialize FastAPI
# -------------------------------
app = FastAPI(
    title="Forensic Accounting API",
    description="AI-powered financial fraud detection system",
    version="1.0.0",
    lifespan=lifespan
)


# -------------------------------
# Register Routes
# -------------------------------
app.include_router(auth.router)
app.include_router(fraud.router)
app.include_router(transactions.router)
app.include_router(financial.router)
app.include_router(reports.router)
app.include_router(analysis.router)


# -------------------------------
# Root Endpoint (Health Check)
# -------------------------------
@app.get("/")
async def root():
    return {
        "message": "Forensic Accounting API is running 🚀",
        "database": settings.DB_NAME
    }