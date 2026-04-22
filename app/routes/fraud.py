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

    doc = await transactions_collection.find_one({"_id": oid, "user_id": current_user["user_id"]})
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
    query = {
        "user_id": current_user["user_id"],
        "$or": [
            {"is_flagged": True},
            {"is_fraud": True},
        ],
    }

    cursor = transactions_collection.find(query)
    docs = await cursor.to_list(length=500)
    return {
        "flagged_transactions": [_serialize_transaction(d) for d in docs],
        "count": len(docs),
    }