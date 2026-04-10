import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.database.collections import audit_logs_collection


# -------------------------------
# CREATE AUDIT LOG (STANDARDIZED)
# -------------------------------
async def create_audit_log(
    *,
    action: str,               # CREATE / UPDATE / DELETE
    user_id: str,
    entity: str,               # e.g. "transaction", "user"
    entity_id: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    success: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:

    entry = {
        "action": action.upper(),
        "user_id": user_id,
        "entity": entity,
        "entity_id": entity_id,
        "changes": changes or {},
        "success": success,
        "metadata": metadata or {},
        "timestamp": datetime.datetime.utcnow(),
    }

    result = await audit_logs_collection.insert_one(entry)
    return str(result.inserted_id)


# -------------------------------
# SERIALIZER
# -------------------------------
def _serialize_audit_log(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# -------------------------------
# GET SINGLE LOG
# -------------------------------
async def get_audit_log_by_id(audit_log_id: str) -> Optional[Dict[str, Any]]:
    oid = ObjectId(audit_log_id)
    doc = await audit_logs_collection.find_one({"_id": oid})
    if not doc:
        return None
    return _serialize_audit_log(doc)


# -------------------------------
# LIST LOGS (FILTERABLE)
# -------------------------------
async def list_audit_logs(
    skip: int = 0,
    limit: int = 50,
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    entity: Optional[str] = None,
    success: Optional[bool] = None,
    min_date: Optional[datetime.datetime] = None,
    max_date: Optional[datetime.datetime] = None,
) -> List[Dict[str, Any]]:

    query: Dict[str, Any] = {}

    if action:
        query["action"] = action.upper()

    if user_id:
        query["user_id"] = user_id

    if entity:
        query["entity"] = entity

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

    return [_serialize_audit_log(d) for d in docs]