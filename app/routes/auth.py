import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel, EmailStr
from typing import Literal
from bson import ObjectId
from app.services.user_service import get_user_by_email, create_user
from app.services.audit_service import create_audit_log
from app.database.collections import audit_logs_collection
from app.database.collections import users_collection
from app.utils.dependencies import get_current_user
from app.utils.password import verify_password, hash_password
from app.utils.jwt import create_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Optional bearer dependency for endpoints like logout where a missing/invalid
# token should not prevent the action from completing.
optional_bearer = HTTPBearer(auto_error=False)


# =========================
# SCHEMAS
# =========================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: Literal["admin", "auditor", "management"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _serialize_audit_log(doc: dict) -> dict:
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# =========================
# SIGNUP
# =========================

@router.post("/register", response_model=AuthResponse)
async def register(data: RegisterRequest):

    # Check if user already exists
    existing_user = await get_user_by_email(data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash password
    hashed_password = hash_password(data.password)

    # Create user object
    role = data.role.strip().lower()
    user_data = {
        "email": data.email,
        "password": hash_password(data.password),
        "role": role,
        "is_logged_in": False,
        "created_at": datetime.datetime.utcnow(),
    }

    # Save to DB
    result = await create_user(user_data)

    # Generate token immediately after signup
    token = create_token({
        "user_id": str(result["_id"]),
        "role": role
    })

    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer)
):
    """Logout endpoint: attempt to decode the bearer token if present and
    mark the user as logged out. If no token is provided (common from some
    frontends), return OK without raising 401 so the UI can clear client state.
    """
    user_id = None
    role = None

    if credentials and credentials.credentials:
        token = credentials.credentials
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("user_id")
            role = payload.get("role")
        except Exception:
            # Don't fail logout if token is invalid/expired; just proceed to return OK
            user_id = None

    if user_id:
        now = datetime.datetime.utcnow()
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_logged_in": False, "updated_at": now}},
        )

        await create_audit_log(
            action="LOGOUT",
            user_id=str(user_id),
            entity="user",
            entity_id=str(user_id),
            metadata={"user_id": str(user_id), "role": role},
        )

    return {"ok": True}


@router.get("/recent-logins")
@router.get("/recent-logins/")
async def recent_logins_alias(
    limit: int = Query(20, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    cursor = audit_logs_collection.find(
        {"action": "LOGIN", "entity": "user"}
    ).sort("timestamp", -1).limit(limit)

    docs = await cursor.to_list(length=limit)
    return {"recent_logins": [_serialize_audit_log(d) for d in docs], "count": len(docs)}


@router.get("/login-history")
@router.get("/login-history/")
async def login_history_alias(
    limit: int = Query(20, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    return await recent_logins_alias(limit=limit, current_user=current_user)


# =========================
# LOGIN
# =========================

@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest):
    user = await get_user_by_email(data.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    hashed_password = user.get("password")
    role = (user.get("role") or "").strip().lower()

    if role not in {"admin", "auditor", "management"}:
        raise HTTPException(status_code=403, detail="User role is invalid")

    if not hashed_password or not role or not verify_password(data.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "user_id": str(user["_id"]),
        "role": role
    })

    now = datetime.datetime.utcnow()
    await users_collection.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"is_logged_in": True, "last_login": now, "updated_at": now}},
    )

    await create_audit_log(
        action="LOGIN",
        user_id=str(user["_id"]),
        entity="user",
        entity_id=str(user["_id"]),
        metadata={"email": data.email, "role": role},
    )

    return {"access_token": token, "token_type": "bearer"}