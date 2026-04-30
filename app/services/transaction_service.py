# app/services/transaction_service.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from app.database.collections import transactions_collection
from app.services.fraud_detection import detect_fraud
from app.services.audit_service import create_audit_log


def _serialize_transaction(doc: dict) -> dict:
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    # Normalize common field names to the API's response aliases expected by Pydantic
    # Ensure the response includes alias keys like 'Date', 'Amount', 'Note', etc.
    try:
        # transaction_date -> Date
        if "transaction_date" in doc and "Date" not in doc:
            td = doc.get("transaction_date")
            if isinstance(td, datetime):
                doc["Date"] = td.isoformat()
            else:
                doc["Date"] = str(td)

        # lower-case date -> Date
        if "date" in doc and "Date" not in doc:
            d = doc.get("date")
            if isinstance(d, datetime):
                doc["Date"] = d.isoformat()
            else:
                doc["Date"] = str(d)

        # amount -> Amount
        if "amount" in doc and "Amount" not in doc:
            doc["Amount"] = doc.get("amount")

        # description -> Note
        if "description" in doc and "Note" not in doc:
            doc["Note"] = doc.get("description")

        # map other common fields to expected aliases if present
        mappings = {
            "category": "Category",
            "currency": "Currency",
            "mode": "Mode",
            "subcategory": "Subcategory",
            "note": "Note",
        }

        for src, alias in mappings.items():
            if src in doc and alias not in doc:
                doc[alias] = doc.get(src)
    except Exception:
        # Best-effort mapping; avoid raising during serialization
        pass

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
    # Mark transaction as flagged when analysis indicates fraud or ML flagged anomaly
    ml_info = fraud_result.get("ml_score") or {}
    ml_flag = ml_info.get("ml_flag") if isinstance(ml_info, dict) else False
    transaction["is_flagged"] = bool(fraud_result.get("is_fraud", False) or ml_flag)

    result = await transactions_collection.insert_one(transaction)

    created = await transactions_collection.find_one({"_id": result.inserted_id})
    if not created:
        raise RuntimeError("Failed to create transaction")

    # 🔥 AUDIT LOG
    await create_audit_log(**{
        "user_id": user_id,
        "action": "CREATE",
        "entity": "transaction",
        "entity_id": str(result.inserted_id),
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
    is_flagged: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
):
    # NOTE: Removed per-user filtering so queries return global data
    query: Dict[str, Any] = {}

    if is_flagged is not None:
        query["is_flagged"] = is_flagged

    if min_amount is not None or max_amount is not None:
        query["Amount"] = {}
        if min_amount is not None:
            query["Amount"]["$gte"] = min_amount
        if max_amount is not None:
            query["Amount"]["$lte"] = max_amount

    cursor = transactions_collection.find(query).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_serialize_transaction(d) for d in docs]


# =========================
# GET TRANSACTION
# =========================
async def get_transaction_by_id(transaction_id: str, user_id: Optional[str] = None) -> Optional[dict]:
    oid = _parse_object_id(transaction_id)

    query: Dict[str, Any] = {"_id": oid}
    if user_id:
        query["user_id"] = user_id

    doc = await transactions_collection.find_one(query)

    if not doc:
        return None

    return _serialize_transaction(doc)


# =========================
# UPDATE TRANSACTION
# =========================
async def update_transaction(transaction_id: str, update_fields: dict, user_id: str):
    oid = _parse_object_id(transaction_id)

    # Get old data (for audit)
    # Allow global updates: do not restrict by `user_id`
    old_doc = await transactions_collection.find_one({
        "_id": oid
    })

    if not old_doc:
        return None

    # Ensure consistency: if `is_fraud` is being set to a truthy value,
    # also mark the transaction as flagged unless the caller explicitly sets `is_flagged`.
    try:
        incoming_is_fraud = update_fields.get("is_fraud")
    except Exception:
        incoming_is_fraud = None

    if incoming_is_fraud:
        if "is_flagged" not in update_fields:
            update_fields["is_flagged"] = True

    result = await transactions_collection.update_one(
        {"_id": oid},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return None

    updated_doc = await transactions_collection.find_one({"_id": oid})

    # 🔥 AUDIT LOG (track changes)
    await create_audit_log(**{
        "user_id": user_id,
        "action": "UPDATE",
        "entity": "transaction",
        "entity_id": transaction_id,
        "changes": {
            "before": _serialize_transaction(old_doc),
            "after": _serialize_transaction(updated_doc)
        }
    })

    return _serialize_transaction(updated_doc)


async def sync_flagged_from_fraud(batch_size: int = 1000) -> dict:
    """One-off utility: set `is_flagged=True` for any document where `is_fraud` is truthy.

    Returns a summary dict with counts. This is intentionally an async utility the
    operator can run in a REPL or task runner to retroactively fix existing records.
    """
    query = {"is_fraud": {"$in": [True, "true", "True", 1, "1"]}}
    cursor = transactions_collection.find(query).batch_size(batch_size)
    updated = 0
    async for doc in cursor:
        _id = doc.get("_id")
        if not doc.get("is_flagged"):
            res = await transactions_collection.update_one({"_id": _id}, {"$set": {"is_flagged": True}})
            if res.modified_count > 0:
                updated += 1

    return {"updated": updated}


# =========================
# DELETE TRANSACTION
# =========================
async def delete_transaction(transaction_id: str, user_id: str) -> bool:
    oid = _parse_object_id(transaction_id)

    # Get data before delete
    doc = await transactions_collection.find_one({"_id": oid})

    if not doc:
        return False

    result = await transactions_collection.delete_one({"_id": oid})

    if result.deleted_count == 0:
        return False

    # 🔥 AUDIT LOG
    await create_audit_log(**{
        "user_id": user_id,
        "action": "DELETE",
        "entity": "transaction",
        "entity_id": transaction_id,
        "changes": _serialize_transaction(doc)
    })

    return True


# =========================
# BULK IMPORT TRANSACTIONS
# =========================
async def bulk_import_transactions(
    transactions: List[dict],
    user_id: str,
    *,
    batch_size: int = 1000,
) -> Dict[str, Any]:
    inserted = 0
    if not transactions:
        return {"inserted": 0, "batches": 0}

    batches = 0
    now = datetime.utcnow()

    for i in range(0, len(transactions), batch_size):
        chunk = [t.copy() for t in transactions[i : i + batch_size]]
        for doc in chunk:
            doc["user_id"] = user_id
            doc.setdefault("timestamp", now)

        result = await transactions_collection.insert_many(chunk, ordered=False)
        inserted += len(result.inserted_ids)
        batches += 1

    return {"inserted": inserted, "batches": batches}