from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.user_service import get_user_by_email
from app.utils.password import verify_password
from app.utils.jwt import create_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Pydantic schema for login request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Pydantic schema for login response
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    # Fetch user from DB
    user = await get_user_by_email(data.email)

    # Verify password
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token
    token = create_token({
        "user_id": str(user["_id"]),
        "role": user["role"]
    })

    return {"access_token": token, "token_type": "bearer"}