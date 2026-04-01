# app/config/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

# Connect to MongoDB
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]