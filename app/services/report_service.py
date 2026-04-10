from typing import Dict
from app.database.collections import transactions_collection


# =========================
# FRAUD SUMMARY REPORT
# =========================
async def fraud_summary(user_id: str) -> Dict:
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": None,
                "total_transactions": {"$sum": 1},
                "fraud_count": {
                    "$sum": {
                        "$cond": ["$is_fraud", 1, 0]
                    }
                },
                "total_amount": {"$sum": "$amount"},
                "fraud_amount": {
                    "$sum": {
                        "$cond": ["$is_fraud", "$amount", 0]
                    }
                }
            }
        }
    ]

    result = await transactions_collection.aggregate(pipeline).to_list(1)

    if not result:
        return {
            "total_transactions": 0,
            "fraud_count": 0,
            "fraud_rate": 0,
            "total_amount": 0,
            "fraud_amount": 0
        }

    data = result[0]

    return {
        "total_transactions": data["total_transactions"],
        "fraud_count": data["fraud_count"],
        "fraud_rate": (
            data["fraud_count"] / data["total_transactions"]
            if data["total_transactions"] > 0 else 0
        ),
        "total_amount": data["total_amount"],
        "fraud_amount": data["fraud_amount"]
    }


# =========================
# RISK ANALYSIS REPORT
# =========================
async def risk_analysis(user_id: str) -> Dict:
    transactions = await transactions_collection.find(
        {"user_id": user_id}
    ).to_list(1000)

    if not transactions:
        return {
            "avg_risk_score": 0,
            "high_risk_transactions": 0,
            "medium_risk_transactions": 0,
            "low_risk_transactions": 0
        }

    total_risk = 0
    high = 0
    medium = 0
    low = 0

    for tx in transactions:
        score = tx.get("risk_score", 0)
        total_risk += score

        if score >= 70:
            high += 1
        elif score >= 40:
            medium += 1
        else:
            low += 1

    return {
        "avg_risk_score": total_risk / len(transactions),
        "high_risk_transactions": high,
        "medium_risk_transactions": medium,
        "low_risk_transactions": low,
        "total_transactions": len(transactions)
    }