# app/services/transaction_service.py
from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId
from app.database.collections import transactions_collection
from app.services.fraud_detection import detect_fraud
from app.services.audit_service import create_audit_log


def _serialize_transaction(doc: dict) -> dict:
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def _parse_object_id(transaction_id: str) -> ObjectId:
    return ObjectId(transaction_id)


# =========================
# CREATE TRANSACTION
# =========================
async def create_transaction(transaction: dict, user_id: str) -> dict:
    transaction = transaction.copy()
    transaction["timestamp"] = datetime.utcnow()
    transaction["user_id"] = user_id

    # Get recent transactions
    recent_transactions = await transactions_collection.find(
        {"user_id": user_id}
    ).to_list(10)

    # Fraud detection
    fraud_result = detect_fraud(transaction, recent_transactions)
    transaction["is_fraud"] = fraud_result.get("is_fraud", False)
    transaction["risk_score"] = fraud_result.get("risk_score", 0)
    transaction["fraud_reasons"] = fraud_result.get("reasons", [])

    result = await transactions_collection.insert_one(transaction)

    created = await transactions_collection.find_one({"_id": result.inserted_id})
    if not created:
        raise RuntimeError("Failed to create transaction")

    # 🔥 AUDIT LOG
    await create_audit_log({
        "user_id": user_id,
        "action": "CREATE",
        "entity": "transaction",
        "entity_id": str(result.inserted_id),
        "timestamp": datetime.utcnow(),
        "changes": transaction
    })

    return _serialize_transaction(created)


# =========================
# LIST TRANSACTIONS
# =========================
async def list_transactions(
    *,
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[str] = None,
):
    query: Dict[str, Any] = {}

    if user_id:
        query["user_id"] = user_id

    cursor = transactions_collection.find(query).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_serialize_transaction(d) for d in docs]


# =========================
# GET TRANSACTION
# =========================
async def get_transaction_by_id(transaction_id: str, user_id: str) -> Optional[dict]:
    oid = _parse_object_id(transaction_id)

    doc = await transactions_collection.find_one({
        "_id": oid,
        "user_id": user_id
    })

    if not doc:
        return None

    return _serialize_transaction(doc)


# =========================
# UPDATE TRANSACTION
# =========================
async def update_transaction(transaction_id: str, update_fields: dict, user_id: str):
    oid = _parse_object_id(transaction_id)

    # Get old data (for audit)
    old_doc = await transactions_collection.find_one({
        "_id": oid,
        "user_id": user_id
    })

    if not old_doc:
        return None

    result = await transactions_collection.update_one(
        {"_id": oid, "user_id": user_id},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return None

    updated_doc = await transactions_collection.find_one({"_id": oid})

    # 🔥 AUDIT LOG (track changes)
    await create_audit_log({
        "user_id": user_id,
        "action": "UPDATE",
        "entity": "transaction",
        "entity_id": transaction_id,
        "timestamp": datetime.utcnow(),
        "changes": {
            "before": _serialize_transaction(old_doc),
            "after": _serialize_transaction(updated_doc)
        }
    })

    return _serialize_transaction(updated_doc)


# =========================
# DELETE TRANSACTION
# =========================
async def delete_transaction(transaction_id: str, user_id: str) -> bool:
    oid = _parse_object_id(transaction_id)

    # Get data before delete
    doc = await transactions_collection.find_one({
        "_id": oid,
        "user_id": user_id
    })

    if not doc:
        return False

    result = await transactions_collection.delete_one({
        "_id": oid,
        "user_id": user_id
    })

    if result.deleted_count == 0:
        return False

    # 🔥 AUDIT LOG
    await create_audit_log({
        "user_id": user_id,
        "action": "DELETE",
        "entity": "transaction",
        "entity_id": transaction_id,
        "timestamp": datetime.utcnow(),
        "changes": _serialize_transaction(doc)
    })

    return True