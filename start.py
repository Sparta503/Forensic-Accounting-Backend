import uvicorn
from app.main import app as fastapi_app
import sys

if __name__ == "__main__":
    try:
        uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, reload=False)
    finally:
        if getattr(sys, "frozen", False):
            input("Press Enter to close...")