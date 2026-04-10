# app/services/ml_fraud_model.py

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from pathlib import Path

MODEL_PATH = Path("ml_model.pkl")


class FraudIsolationModel:
    def __init__(self):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )
        self.is_trained = False

    def train(self, transactions: list):
        if len(transactions) < 20:
            raise ValueError("Need at least 20 transactions to train model")

        X = np.array([
            [
                tx.get("amount", 0),
                len(tx.get("description", "")),
                1 if tx.get("is_flagged") else 0
            ]
            for tx in transactions
        ])

        self.model.fit(X)
        self.is_trained = True

        joblib.dump(self.model, MODEL_PATH)

    def load(self):
        if MODEL_PATH.exists():
            self.model = joblib.load(MODEL_PATH)
            self.is_trained = True

    def predict(self, transaction: dict):
        if not self.is_trained:
            self.load()

        X = np.array([[
            transaction.get("amount", 0),
            len(transaction.get("description", "")),
            1 if transaction.get("is_flagged") else 0
        ]])

        score = self.model.decision_function(X)[0]
        prediction = self.model.predict(X)[0]

        return {
            "ml_score": float(score),
            "is_anomaly": prediction == -1
        }


# =========================
# 🔥 ADD THIS (THE FIX)
# =========================
ml_model = FraudIsolationModel()