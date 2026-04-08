# app/services/transaction_service.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from app.database.collections import transactions_collection
from app.services.fraud_detection import detect_fraud


def _serialize_transaction(doc: dict) -> dict:
    """Convert ObjectId to string and return a copy."""
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def _parse_object_id(transaction_id: str) -> ObjectId:
    """Convert string ID to ObjectId."""
    return ObjectId(transaction_id)


async def create_transaction(transaction: dict) -> dict:
    """Create a transaction, run fraud detection, and return serialized transaction."""
    transaction = transaction.copy()
    transaction["timestamp"] = datetime.utcnow()

    user_id = transaction.get("user_id")
    recent_transactions: List[dict] = []
    if user_id:
        recent_transactions = await transactions_collection.find({"user_id": user_id}).to_list(10)

    # Run fraud detection
    fraud_result = detect_fraud(transaction, recent_transactions)
    transaction["is_fraud"] = fraud_result.get("is_fraud", False)
    transaction["risk_score"] = fraud_result.get("risk_score", 0)
    transaction["fraud_reasons"] = fraud_result.get("reasons", [])

    # Insert into DB
    result = await transactions_collection.insert_one(transaction)
    created = await transactions_collection.find_one({"_id": result.inserted_id})
    if not created:
        raise RuntimeError("Failed to create transaction")

    return _serialize_transaction(created)


async def list_transactions(
    *,
    skip: int = 0,
    limit: int = 50,
    is_flagged: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    user_id: Optional[str] = None,  # filter by user
) -> List[dict]:
    query: Dict[str, Any] = {}

    if user_id:
        query["user_id"] = user_id

    if is_flagged is not None:
        query["is_flagged"] = is_flagged

    if min_amount is not None or max_amount is not None:
        query["amount"] = {}
        if min_amount is not None:
            query["amount"]["$gte"] = min_amount
        if max_amount is not None:
            query["amount"]["$lte"] = max_amount

    cursor = transactions_collection.find(query).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_serialize_transaction(d) for d in docs]


async def get_transaction_by_id(transaction_id: str, user_id: Optional[str] = None) -> Optional[dict]:
    """Get a single transaction; optionally enforce ownership by user_id."""
    oid = _parse_object_id(transaction_id)
    query = {"_id": oid}
    if user_id:
        query["user_id"] = user_id

    doc = await transactions_collection.find_one(query)
    if not doc:
        return None
    return _serialize_transaction(doc)


async def update_transaction(transaction_id: str, update_fields: dict, user_id: Optional[str] = None) -> Optional[dict]:
    """Update transaction; optionally enforce ownership by user_id."""
    oid = _parse_object_id(transaction_id)
    query = {"_id": oid}
    if user_id:
        query["user_id"] = user_id

    if not update_fields:
        return await get_transaction_by_id(transaction_id, user_id)

    result = await transactions_collection.update_one(query, {"$set": update_fields})
    if result.matched_count == 0:
        return None

    doc = await transactions_collection.find_one(query)
    if not doc:
        return None
    return _serialize_transaction(doc)


async def delete_transaction(transaction_id: str, user_id: Optional[str] = None) -> bool:
    """Delete transaction; optionally enforce ownership by user_id."""
    oid = _parse_object_id(transaction_id)
    query = {"_id": oid}
    if user_id:
        query["user_id"] = user_id

    result = await transactions_collection.delete_one(query)
    return result.deleted_count > 0