# test_db.py
import asyncio
from app.config.db import db
from app.database.collections import users_collection

async def test():
    # insert a test user
    result = await users_collection.insert_one({"email": "test@example.com", "password": "hashedpassword"})
    print("Inserted user ID:", result.inserted_id)

    # list collections
    collections = await db.list_collection_names()
    print("Collections in DB:", collections)

asyncio.run(test())