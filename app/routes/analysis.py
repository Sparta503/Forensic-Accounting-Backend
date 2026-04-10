from fastapi import APIRouter, Depends
from app.services.financial_analysis import (
    calculate_financial_ratios,
    detect_trends,
    analyze_financials
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/analysis", tags=["analysis"])


# -------------------------
# FULL ANALYSIS
# -------------------------
@router.post("/financial")
async def financial_analysis(data: dict, current_user=Depends(get_current_user)):
    return analyze_financials(
        statement=data["statement"],
        historical_data=data["history"]
    )


# -------------------------
# RATIOS ONLY
# -------------------------
@router.post("/ratios")
async def ratios(data: dict, current_user=Depends(get_current_user)):
    return calculate_financial_ratios(data)


# -------------------------
# TREND ANALYSIS
# -------------------------
@router.post("/trends")
async def trends(data: dict, current_user=Depends(get_current_user)):
    return detect_trends(
        time_series=data["history"],
        field=data["field"]
    )