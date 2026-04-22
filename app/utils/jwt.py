import jwt
from datetime import datetime, timedelta
from app.config.settings import settings

def create_token(data: dict):
    payload = data.copy()
    if settings.JWT_EXPIRES_HOURS > 0:
        payload["exp"] = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRES_HOURS)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")