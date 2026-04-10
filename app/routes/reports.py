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
    return await fraud_summary(current_user["user_id"])


# =========================
# RISK ANALYSIS
# =========================
@router.get("/risk-analysis")
async def get_risk_analysis(
    current_user: dict = Depends(get_current_user)
):
    return await risk_analysis(current_user["user_id"])