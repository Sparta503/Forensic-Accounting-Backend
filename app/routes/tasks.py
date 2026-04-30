import datetime
from typing import Any, Dict, List, Literal, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, validator

from app.database.collections import tasks_collection
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])
management_router = APIRouter(prefix="/management", tags=["tasks"])
department_router = APIRouter(prefix="/department-tasks", tags=["tasks"])


TaskStatus = Literal["pending", "in_progress", "completed"]


def _normalize_status(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"pending", "in_progress", "completed"}:
            return v

        v = v.replace("-", "_")
        v = v.replace(" ", "_")
        if v in {"pending", "in_progress", "completed"}:
            return v

        if v in {"inprogress", "in_progress"}:
            return "in_progress"

    return value


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    department: Optional[str] = None
    due_date: Optional[datetime.datetime] = None
    status: TaskStatus = "pending"

    @validator("status", pre=True)
    def normalize_status(cls, v):
        v = _normalize_status(v)
        return v


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    department: Optional[str] = None
    due_date: Optional[datetime.datetime] = None
    status: Optional[TaskStatus] = None

    @validator("status", pre=True)
    def normalize_status(cls, v):
        v = _normalize_status(v)
        return v


def _serialize_task(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])

    for key in ("created_at", "updated_at", "due_date"):
        if isinstance(doc.get(key), datetime.datetime):
            doc[key] = doc[key].isoformat()

    return doc


@router.get("/")
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[TaskStatus] = None,
    department: Optional[str] = None,
    assigned_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    query: Dict[str, Any] = {}
    if status:
        query["status"] = status
    if department:
        query["department"] = department
    if assigned_to:
        query["assigned_to"] = assigned_to

    cursor = tasks_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return {"tasks": [_serialize_task(d) for d in docs], "count": len(docs)}


@router.post("/")
async def create_task(
    payload: TaskCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    now = datetime.datetime.utcnow()

    doc: Dict[str, Any] = {
        "title": payload.title,
        "description": payload.description,
        "assigned_to": payload.assigned_to,
        "department": payload.department,
        "due_date": payload.due_date,
        "status": payload.status,
        "created_at": now,
        "updated_at": now,
        "created_by": current_user.get("user_id"),
    }

    result = await tasks_collection.insert_one(doc)
    created = await tasks_collection.find_one({"_id": result.inserted_id})
    return _serialize_task(created or {**doc, "_id": result.inserted_id})


@department_router.post("")
@department_router.post("/")
async def create_department_task_alias(
    payload: TaskCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    return await create_task(payload=payload, current_user=current_user)


@department_router.get("")
@department_router.get("/")
async def list_department_tasks_alias(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[TaskStatus] = None,
    department: Optional[str] = None,
    assigned_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    return await list_tasks(
        skip=skip,
        limit=limit,
        status=status,
        department=department,
        assigned_to=assigned_to,
        current_user=current_user,
    )


@router.patch("/{task_id}")
async def update_task(
    task_id: str,
    payload: TaskUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        oid = ObjectId(task_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid task_id") from e

    update: Dict[str, Any] = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="No fields provided")

    update["updated_at"] = datetime.datetime.utcnow()

    result = await tasks_collection.update_one({"_id": oid}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    doc = await tasks_collection.find_one({"_id": oid})
    return _serialize_task(doc or {"_id": oid, **update})


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    try:
        oid = ObjectId(task_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid task_id") from e

    result = await tasks_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"ok": True}


@management_router.get("/tasks")
@management_router.get("/tasks/")
async def management_tasks_alias(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[TaskStatus] = None,
    department: Optional[str] = None,
    assigned_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    return await list_tasks(
        skip=skip,
        limit=limit,
        status=status,
        department=department,
        assigned_to=assigned_to,
        current_user=current_user,
    )
