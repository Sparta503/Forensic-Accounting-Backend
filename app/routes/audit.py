from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query

from app.database.collections import audit_logs_collection
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/audit", tags=["audit"])
logs_router = APIRouter(prefix="/logs", tags=["audit"])


def _serialize_audit_log(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("/recent-logins")
async def recent_logins(
    limit: int = Query(20, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    cursor = audit_logs_collection.find(
        {"action": "LOGIN", "entity": "user"}
    ).sort("timestamp", -1).limit(limit)

    docs = await cursor.to_list(length=limit)
    return {"recent_logins": [_serialize_audit_log(d) for d in docs], "count": len(docs)}


@logs_router.get("/recent-logins")
async def recent_logins_alias(
    limit: int = Query(20, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    return await recent_logins(limit=limit, current_user=current_user)
