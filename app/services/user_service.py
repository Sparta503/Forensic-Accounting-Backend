# app/services/user_service.py

from app.database.collections import users_collection
from typing import Optional
from bson import ObjectId


# =========================
# CREATE USER
# =========================
async def create_user(user: dict) -> dict:
    result = await users_collection.insert_one(user)

    return {
        "_id": str(result.inserted_id),
        "email": user["email"],
        "role": user["role"]
    }


# =========================
# GET USER BY EMAIL
# =========================
async def get_user_by_email(email: str) -> Optional[dict]:
    user = await users_collection.find_one({"email": email})

    if user:
        user["_id"] = str(user["_id"])  # convert ObjectId → string

    return user


# =========================
# GET USER BY ID (useful later)
# =========================
async def get_user_by_id(user_id: str) -> Optional[dict]:
    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    if user:
        user["_id"] = str(user["_id"])

    return user