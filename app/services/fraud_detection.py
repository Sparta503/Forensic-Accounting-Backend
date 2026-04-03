from app.models.fraud_detection import FraudDetectionModel


async def check_fraud(transaction_id: str):
    # Placeholder logic – replace with your actual fraud detection
    fraud_detection_model = await FraudDetectionModel.get(transaction_id=transaction_id)
    if fraud_detection_model:
        is_fraud = fraud_detection_model.is_fraud
    else:
        is_fraud = False
    return {
        "transaction_id": transaction_id,
        "is_fraud": is_fraud,
        "message": "This is just a placeholder. Replace with your actual fraud detection logic."
    }