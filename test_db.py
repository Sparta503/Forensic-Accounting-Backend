# test_db.py
import asyncio
from app.config.db import db
from app.database.collections import users_collection
import random
import string

async def test():
    # insert a test user
    users = [{"email": f"test{i}@example.com", "password": f"test{i}!", "role": "user", "company_name": "Test Company"} for i in range(10)]
    result = await users_collection.insert_many(users)
    print("Inserted user IDs:", list(result.inserted_ids))

    # list collections
    collections = await db.list_collection_names()
    print("Collections in DB:", col