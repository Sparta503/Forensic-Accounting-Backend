import jwt
from datetime import datetime, timedelta
from app.config.settings import settings

def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=2)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")