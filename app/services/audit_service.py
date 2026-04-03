import datetime
from typing import Any, Dict, List, Optional

from pymongo import InsertOne, UpdateOne

from app.database.collections import audit_logs_collection


async def create_audit_log(entry: Dict[str, Any]) -> str:
    result = await audit_logs_collection.insert_one(entry)
    return str(result.inserted_id)


async def get_audit_log_by_id(audit_log_id: str) -> Optional[Dict[str, Any]]:
    oid = ObjectId(audit_log_id)
    doc = await audit_logs_collection.find_one({"_id": oid})
    return doc


async def list_audit_logs(
    skip: int = 0,
    limit: int = 50,
    action: Optional[str] = None,
    success: Optional[bool] = None,
    min_date: Optional[datetime.datetime] = None,
    max_date: Optional[datetime.datetime] = None,
) -> List[Dict[str, Any]]:
    query: Dict[str, Any] = {}

    if action:
        query["action"] = action

    if success is not None:
        query["success"] = success

    if min_date or max_date:
        query["timestamp"] = {}
        if min_date:
            query["timestamp"]["$gte"] = min_date
        if max_date:
            query["timestamp"]["$lte"] = max_date

    cursor = audit_logs_collection.find(query).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return docs