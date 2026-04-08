

from datetime import datetime, timedelta

# Example thresholds (you can move to config later)
MAX_AMOUNT = 10000
MAX_FREQUENCY = 5  # transactions in short time


def detect_fraud(transaction: dict, recent_transactions: list):
    risk_score = 0
    reasons = []

    # 1. Large transaction
    if transaction["amount"] > MAX_AMOUNT:
        risk_score += 50
        reasons.append("High transaction amount")

    # 2. Rapid transactions (velocity check)
    now = datetime.utcnow()
    recent_count = 0

    for tx in recent_transactions:
        tx_time = tx.get("timestamp")
        if tx_time and (now - tx_time) < timedelta(minutes=5):
            recent_count += 1

    if recent_count >= MAX_FREQUENCY:
        risk_score += 30
        reasons.append("High transaction frequency")

    # 3. Suspicious location (example)
    if transaction.get("location") not in ["ZW"]:  # Zimbabwe
        risk_score += 20
        reasons.append("Unusual location")

    # Final decision
    is_fraud = risk_score >= 50

    return {
        "is_fraud": is_fraud,
        "risk_score": risk_score,
        "reasons": reasons
    }