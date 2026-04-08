# app/config/db.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.utils.logger import logger

# Create MongoDB client
client = AsyncIOMotorClient(settings.MONGO_URI)

# Select database
db = client[settings.DB_NAME]

# Safe log (no secrets exposed)
logger.info(f"Connected to {settings.DB_NAME} Database")