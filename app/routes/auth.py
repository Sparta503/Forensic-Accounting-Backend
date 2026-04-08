from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.user_service import get_user_by_email, create_user
from app.utils.password import verify_password, hash_password
from app.utils.jwt import create_token

router = APIRouter(prefix="/auth", tags=["auth"])


# =========================
# SCHEMAS
# =========================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # admin, auditor, analyst


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
    user = {
        "email": data.email,
        "password": hashed_password,
        "role": data.role
    }

    # Save to DB
    result = await create_user(user)

    # Generate token immediately after signup
    token = create_token({
        "user_id": str(user["_id"]),
        "role": user["role"]
    })

    return {"access_token": token, "token_type": "bearer"}


# =========================
# LOGIN
# =========================

@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest):
    user = await get_user_by_email(data.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    hashed_password = user.get("password")
    role = user.get("role")

    if not hashed_password or not role or not verify_password(data.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "user_id": str(user["_id"]),
        "role": role
    })

    return {"access_token": token, "token_type": "bearer"}