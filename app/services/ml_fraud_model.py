# app/services/ml_fraud_model.py

import csv
from datetime import datetime
import numpy as np
import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import IsolationForest
from pathlib import Path
from typing import Optional

MODEL_PATH = Path("ml_model.pkl")


class FraudIsolationModel:
    def __init__(self):
        self.vectorizer = DictVectorizer(sparse=False)
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )
        self.is_trained = False

    def _parse_amount(self, tx: dict) -> float:
        raw = tx.get("Amount", tx.get("amount", 0))
        if raw is None:
            return 0.0
        if isinstance(raw, (int, float)):
            return float(raw)
        raw_str = str(raw).replace(",", "").strip()
        if raw_str == "":
            return 0.0
        try:
            return float(raw_str)
        except Exception:
            return 0.0

    def _parse_date(self, tx: dict) -> Optional[datetime]:
        raw = tx.get("Date", tx.get("date"))
        if raw is None:
            return None
        raw_str = str(raw).strip()
        if raw_str == "":
            return None

        formats = [
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(raw_str, fmt)
            except Exception:
                continue
        return None

    def _feature_dict(self, tx: dict) -> dict:
        amount = self._parse_amount(tx)
        note = tx.get("Note", tx.get("note", ""))
        note_str = "" if note is None else str(note)

        mode = tx.get("Mode", tx.get("mode")) or "UNKNOWN"
        category = tx.get("Category", tx.get("category")) or "UNKNOWN"
        subcategory = tx.get("Subcategory", tx.get("subcategory")) or "UNKNOWN"
        income_expense = tx.get("Income/Expense", tx.get("income_expense")) or "UNKNOWN"
        currency = tx.get("Currency", tx.get("currency")) or "UNKNOWN"

        dt = self._parse_date(tx)
        hour = dt.hour if dt else -1
        dow = dt.weekday() if dt else -1
        month = dt.month if dt else -1

        return {
            "amount": amount,
            "abs_amount": abs(amount),
            "note_len": len(note_str),
            "Mode": str(mode),
            "Category": str(category),
            "Subcategory": str(subcategory),
            "Income/Expense": str(income_expense),
            "Currency": str(currency),
            "hour": hour,
            "day_of_week": dow,
            "month": month,
        }

    def train(self, transactions: list):
        if len(transactions) < 20:
            raise ValueError("Need at least 20 transactions to train model")

        features = [self._feature_dict(tx) for tx in transactions]
        X = self.vectorizer.fit_transform(features)
        self.model.fit(X)
        self.is_trained = True

        joblib.dump({"vectorizer": self.vectorizer, "model": self.model}, MODEL_PATH)

    def train_from_csv(self, csv_path: str):
        transactions = []
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                amount = self._parse_amount(row)
                if amount == 0.0 and str(row.get("Amount", "")).strip() == "":
                    continue
                row["Amount"] = amount
                transactions.append(row)

        self.train(transactions)

    def load(self):
        if MODEL_PATH.exists():
            bundle = joblib.load(MODEL_PATH)
            self.vectorizer = bundle["vectorizer"]
            self.model = bundle["model"]
            self.is_trained = True

    def predict(self, transaction: dict):
        if not self.is_trained:
            self.load()

        features = [self._feature_dict(transaction)]
        X = self.vectorizer.transform(features)

        score = self.model.decision_function(X)[0]
        prediction = self.model.predict(X)[0]

        ml_flag = bool(prediction == -1)

        return {
            "ml_score": float(score),
            "ml_flag": bool(ml_flag),
        }


# =========================
# 🔥 ADD THIS (THE FIX)
# =========================
ml_model = FraudIsolationModel()