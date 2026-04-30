from typing import Any, Dict, List

import datetime

from fastapi import APIRouter, Depends, Query

from app.database.collections import users_collection
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


def _serialize_user(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    doc.pop("password", None)

    for key in ("created_at", "updated_at", "last_login"):
        if isinstance(doc.get(key), (datetime.datetime, datetime.date)):
            doc[key] = doc[key].isoformat()

    is_logged_in = bool(doc.get("is_logged_in", False))
    doc["status"] = "Logged in" if is_logged_in else "Logged out"
    return doc


@router.get("/")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=5000),
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    cursor = users_collection.find({}).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_serialize_user(d) for d in docs]
