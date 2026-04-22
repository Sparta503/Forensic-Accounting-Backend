from fastapi import APIRouter, HTTPException
from typing import List, Optional

from pydantic import BaseModel

from app.services.financial_analysis import (
    calculate_financial_ratios,
    detect_trends,
    validate_financial_statement
)

router = APIRouter(prefix="/financial", tags=["financial-analysis"])

class FinancialStatementIn(BaseModel):
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    equity: Optional[float] = None

class FinancialHistoryEntry(BaseModel):
    revenue: Optional[float] = None
    net_income: Optional[float] = None


# -------------------------------
# 1. Financial Ratios
# -------------------------------
@router.post("/ratios")
async def get_ratios(data: FinancialStatementIn):
    try:
        ratios = calculate_financial_ratios(data.dict(exclude_none=True))
        return {
            "message": "Financial ratios calculated successfully",
            "ratios": ratios
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------------
# 2. Trend Detection
# -------------------------------
@router.post("/trends")
async def get_trends(data: List[FinancialHistoryEntry]):
    try:
        history = [d.dict(exclude_none=True) for d in data]
        trends = {
            "revenue": detect_trends(history, "revenue"),
            "income": detect_trends(history, "net_income")
        }

        return {
            "message": "Trend analysis complete",
            "trends": trends
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------------
# 3. Financial Statement Validation
# -------------------------------
@router.post("/validate")
async def validate_statement(data: FinancialStatementIn):
    try:
        result = validate_financial_statement(data.dict(exclude_none=True))
        return {
            "message": "Validation complete",
            "validation": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))