from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.financial_analysis import (
    calculate_financial_ratios,
    detect_trends,
    analyze_financials
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/analysis", tags=["analysis"])

class FinancialAnalysisRequest(BaseModel):
    statement: Dict[str, float]
    history: List[Dict[str, Any]]
    transaction: Dict[str, Any] = {}

class TrendsRequest(BaseModel):
    history: List[Dict[str, Any]]
    field: str

# -------------------------
# FULL ANALYSIS
# -------------------------
@router.post("/financial")
async def financial_analysis(data: FinancialAnalysisRequest, current_user=Depends(get_current_user)):
    return analyze_financials(
        statement=data.statement,
        history=data.history,
        transaction=data.transaction
    )

# -------------------------
# RATIOS ONLY
# -------------------------
@router.post("/ratios")
async def ratios(data: Dict[str, float], current_user=Depends(get_current_user)):
    return calculate_financial_ratios(data)

# -------------------------
# TREND ANALYSIS
# -------------------------
@router.post("/trends")
async def trends(data: TrendsRequest, current_user=Depends(get_current_user)):
    return detect_trends(
        time_series=data.history,
        field=data.field
    )