import asyncio
import traceback
import sys
from pathlib import Path

# Ensure repo root is on sys.path so `import app` works when running this script
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from app.services.transaction_service import sync_flagged_from_fraud


async def main():
    try:
        res = await sync_flagged_from_fraud()
        print(res)
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
