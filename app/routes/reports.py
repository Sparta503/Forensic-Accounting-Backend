from fastapi import APIRouter, Depends

from app.utils.dependencies import get_current_user
from app.services.report_service import fraud_summary, risk_analysis

router = APIRouter(prefix="/reports", tags=["reports"])


# =========================
# FRAUD SUMMARY
# =========================
@router.get("/fraud-summary")
async def get_fraud_summary(
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role", "")
    target_user = None if role in ("admin", "management") else current_user["user_id"]
    return await fraud_summary(target_user)


# =========================
# RISK ANALYSIS
# =========================
@router.get("/risk-analysis")
async def get_risk_analysis(
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role", "")
    target_user = None if role in ("admin", "management") else current_user["user_id"]
    return await risk_analysis(target_user)