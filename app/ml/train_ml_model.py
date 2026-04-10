import numpy as np
import joblib
from app.database.collections import transactions_collection
from sklearn.ensemble import IsolationForest


# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
def build_features(transactions):
    features = []

    for tx in transactions:
        features.append([
            float(tx.get("amount", 0)),
            1 if tx.get("is_flagged") else 0,
            len(tx.get("fraud_reasons", [])),
        ])

    return np.array(features)


# -----------------------------
# TRAIN MODEL
# -----------------------------
async def train_model():
    print("Loading data...")

    data = await transactions_collection.find({}).to_list(1000)

    if len(data) < 20:
        print("Not enough data to train")
        return

    X = build_features(data)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    model.fit(X)

    joblib.dump(model, "ml_model.pkl")

    print("Model trained and saved successfully!")


# Run manually
if __name__ == "__main__":
    import asyncio
    asyncio.run(train_model())