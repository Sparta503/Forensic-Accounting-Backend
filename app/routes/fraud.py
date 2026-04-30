# app/routes/fraud.py
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database.collections import transactions_collection
from app.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/fraud",
    tags=["fraud"]
)


def _serialize_transaction(doc: dict) -> dict:
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# Example route: check if a transaction is fraudulent
@router.get("/check/{transaction_id}")
async def check_fraud(transaction_id: str, current_user: dict = Depends(get_current_user)):
    try:
        oid = ObjectId(transaction_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid transaction_id") from e

    # Allow global check by id (do not restrict by user)
    doc = await transactions_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")

    doc = _serialize_transaction(doc)
    return {
        "transaction_id": transaction_id,
        "is_fraud": doc.get("is_fraud"),
        "risk_score": doc.get("risk_score"),
        "fraud_reasons": doc.get("fraud_reasons"),
    }

# Example route: list all flagged transactions
@router.get("/flagged")
async def flagged_transactions(current_user: dict = Depends(get_current_user)):
    # Return flagged transactions globally (no per-user restriction)
    query = {
        "$or": [
            {"is_flagged": True},
            {"is_fraud": True},
        ],
    }

    cursor = transactions_collection.find(query)
    docs = await cursor.to_list(length=500)

    def _risk_level_from_score(score: int | None) -> str:
        try:
            s = int(score or 0)
        except Exception:
            return "Unknown"
        if s <= 20:
            return "Low"
        if s <= 50:
            return "Medium"
        if s <= 80:
            return "High"
        return "Critical"

    transformed = []
    for d in docs:
        doc = _serialize_transaction(d)
        tid = doc.get("_id")
        risk_score = doc.get("risk_score")
        is_fraud = doc.get("is_fraud")
        is_flagged = doc.get("is_flagged")
        reasons = doc.get("fraud_reasons") or []

        # short reason summary (top two) vs full fraud reasons list
        if reasons:
            reason_summary = ", ".join(reasons[:2]) if len(reasons) > 2 else ", ".join(reasons)
        else:
            reason_summary = "-"

        # timestamp formatting
        ts = doc.get("timestamp")
        try:
            if hasattr(ts, "isoformat"):
                ts_str = ts.isoformat()
            else:
                ts_str = str(ts) if ts is not None else "-"
        except Exception:
            ts_str = "-"

        status = "OK"
        if is_fraud:
            status = "Fraud"
        elif is_flagged:
            status = "Flagged"

        transformed.append({
            "transaction_id": tid,
            "risk_score": risk_score if risk_score is not None else "-",
            "risk": risk_score if risk_score is not None else "-",
            "risk_level": _risk_level_from_score(risk_score),
            "status": status,
            "reason": reason_summary,
            "fraud_reasons": reasons,
            "timestamp": ts_str,
        })

    return {
        "flagged_transactions": transformed,
        "count": len(transformed),
    }