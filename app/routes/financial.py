from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.services.financial_analysis import (
    calculate_financial_ratios,
    detect_trends,
    validate_financial_statement
)

router = APIRouter(prefix="/financial", tags=["financial-analysis"])


# -------------------------------
# 1. Financial Ratios
# -------------------------------
@router.post("/ratios")
async def get_ratios(data: Dict[str, Any]):
    try:
        ratios = calculate_financial_ratios(data)
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
async def get_trends(data: List[Dict[str, Any]]):
    try:
        trends = {
            "revenue": detect_trends(data, "revenue"),
            "income": detect_trends(data, "net_income")
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
async def validate_statement(data: Dict[str, Any]):
    try:
        result = validate_financial_statement(data)
        return {
            "message": "Validation complete",
            "validation": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))