from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from app.config.settings import settings

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload  # contains user_id + role
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token expired") from e
    except InvalidSignatureError as e:
        raise HTTPException(status_code=401, detail="Invalid token signature") from e
    except DecodeError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e