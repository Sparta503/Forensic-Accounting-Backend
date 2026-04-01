from app.database.collections import users_collection
from bson import ObjectId
from typing import Optional

# Create a new user
async def create_user(user: dict):
    result = await users_collection.insert_one(user)
    return str(result.inserted_id)

# Get user by email
async def get_user_by_email(email: str) -> Optional[dict]:
    user = await users_collection.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])  # convert ObjectId to string
    return user