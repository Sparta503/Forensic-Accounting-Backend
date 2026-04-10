from datetime import datetime, timedelta
import statistics

from app.services.ml_fraud_model import ml_model


# -------------------------------
# CONFIG
# -------------------------------
MAX_AMOUNT = 10000
MAX_FREQUENCY = 5
Z_SCORE_THRESHOLD = 2.5


# -------------------------------
# Z-SCORE
# -------------------------------
def calculate_z_score(value, data):
    if len(data) < 2:
        return 0

    mean = statistics.mean(data)
    std_dev = statistics.stdev(data)

    if std_dev == 0:
        return 0

    return (value - mean) / std_dev


# -------------------------------
# IQR OUTLIER
# -------------------------------
def detect_outlier_iqr(value, data):
    if len(data) < 4:
        return False

    sorted_data = sorted(data)
    q1 = sorted_data[len(data) // 4]
    q3 = sorted_data[(len(data) * 3) // 4]

    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return value < lower or value > upper


# -------------------------------
# ML SCORE EXTRACTION
# -------------------------------
def ml_score(transaction: dict) -> dict:
    """
    Calls Isolation Forest model
    """
    return ml_model.predict(transaction)


# -------------------------------
# MAIN FRAUD DETECTION ENGINE (HYBRID)
# -------------------------------
def detect_fraud(transaction: dict, recent_transactions: list):

    risk_score = 0
    reasons = []

    amount = transaction.get("amount", 0)

    # -------------------------------
    # 1. RULE: Large transaction
    # -------------------------------
    if amount > MAX_AMOUNT:
        risk_score += 30
        reasons.append("High transaction amount")

    # -------------------------------
    # 2. VELOCITY CHECK
    # -------------------------------
    now = datetime.utcnow()
    recent_count = 0

    for tx in recent_transactions:
        tx_time = tx.get("timestamp")
        if tx_time and (now - tx_time) < timedelta(minutes=5):
            recent_count += 1

    if recent_count >= MAX_FREQUENCY:
        risk_score += 20
        reasons.append("High transaction frequency")

    # -------------------------------
    # 3. LOCATION RULE
    # -------------------------------
    if transaction.get("location") not in ["ZW"]:
        risk_score += 10
        reasons.append("Unusual location")

    # -------------------------------
    # 4. Z-SCORE DETECTION
    # -------------------------------
    amounts = [tx.get("amount", 0) for tx in recent_transactions if "amount" in tx]

    if amounts:
        z = calculate_z_score(amount, amounts)

        if abs(z) > Z_SCORE_THRESHOLD:
            risk_score += 20
            reasons.append(f"Z-score anomaly ({round(z, 2)})")

    # -------------------------------
    # 5. IQR OUTLIER
    # -------------------------------
    if amounts and detect_outlier_iqr(amount, amounts):
        risk_score += 15
        reasons.append("IQR statistical outlier")

    # -------------------------------
    # 6. 🧠 ML MODEL SCORE (NEW)
    # -------------------------------
    ml_result = ml_score(transaction)

    if ml_result["ml_flag"]:
        risk_score += 35
        reasons.append("ML anomaly detection (Isolation Forest)")

    # -------------------------------
    # FINAL DECISION
    # -------------------------------
    is_fraud = risk_score >= 50

    return {
        "is_fraud": is_fraud,
        "risk_score": min(risk_score, 100),
        "reasons": reasons,
        "ml_score": ml_result
    }