from typing import Dict, List, Any
from statistics import mean


# -----------------------------------
# 📊 RATIOS
# -----------------------------------

def calculate_financial_ratios(data: Dict[str, float]) -> Dict[str, float]:
    ratios = {}

    try:
        if data.get("revenue"):
            ratios["profit_margin"] = data["net_income"] / data["revenue"]

        if data.get("current_liabilities"):
            ratios["current_ratio"] = data["current_assets"] / data["current_liabilities"]

        if data.get("total_assets"):
            ratios["debt_ratio"] = data["total_liabilities"] / data["total_assets"]

        if data.get("total_assets"):
            ratios["asset_turnover"] = data["revenue"] / data["total_assets"]

    except Exception:
        pass

    return ratios


# -----------------------------------
# 📈 TREND DETECTION
# -----------------------------------

def detect_trends(time_series: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
    values = [entry.get(field, 0) for entry in time_series]

    if len(values) < 2:
        return {"trend": "insufficient_data"}

    growth = (values[-1] - values[0]) / (abs(values[0]) + 1e-6)

    return {
        "trend": "increase" if growth > 0 else "decrease",
        "growth_rate": growth,
        "average": mean(values)
    }


# -----------------------------------
# 🚨 VALIDATION
# -----------------------------------

def validate_financial_statement(data: Dict[str, float]) -> Dict[str, Any]:
    issues = []

    if data.get("total_assets") != (
        data.get("total_liabilities", 0) + data.get("equity", 0)
    ):
        issues.append("Balance sheet mismatch")

    ratios = calculate_financial_ratios(data)

    if ratios.get("current_ratio", 1) < 1:
        issues.append("Liquidity risk")

    if ratios.get("debt_ratio", 0) > 0.8:
        issues.append("High leverage risk")

    return {
        "issues": issues,
        "ratios": ratios,
        "is_valid": len(issues) == 0
    }


# -----------------------------------
# 🧠 ML FRAUD LAYER (FIXED)
# -----------------------------------

def ml_analyze(transaction: Dict[str, Any]) -> Dict[str, Any]:
    from app.services.ml_fraud_model import ml_model  # lazy import fix

    return ml_model.predict(transaction)


# -----------------------------------
# 🔥 FULL ANALYSIS ENGINE
# -----------------------------------

def analyze_financials(
    statement: Dict[str, float],
    history: List[Dict[str, Any]],
    transaction: Dict[str, Any]
):

    ratios = calculate_financial_ratios(statement)

    trends = {
        "revenue": detect_trends(history, "revenue"),
        "income": detect_trends(history, "net_income")
    }

    validation = validate_financial_statement(statement)

    ml_result = ml_analyze(transaction)

    return {
        "ratios": ratios,
        "trends": trends,
        "validation": validation,
        "ml_detection": ml_result
    }