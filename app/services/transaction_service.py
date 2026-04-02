from typing import Any, Dict, List, Optional
 
from bson import ObjectId
 
from app.database.collections import transactions_collection
 
 
def _serialize_transaction(doc: dict) -> dict:
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc
 
 
def _parse_object_id(transaction_id: str) -> ObjectId:
    return ObjectId(transaction_id)
 
 
async def create_transaction(transaction: dict) -> dict:
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
) -> List[dict]:
    query: Dict[str, Any] = {}
 
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
 
 
async def get_transaction_by_id(transaction_id: str) -> Optional[dict]:
    oid = _parse_object_id(transaction_id)
    doc = await transactions_collection.find_one({"_id": oid})
    if not doc:
        return None
    return _serialize_transaction(doc)
 
 
async def update_transaction(transaction_id: str, update_fields: dict) -> Optional[dict]:
    oid = _parse_object_id(transaction_id)
 
    if not update_fields:
        return await get_transaction_by_id(transaction_id)
 
    result = await transactions_collection.update_one({"_id": oid}, {"$set": update_fields})
    if result.matched_count == 0:
        return None
 
    doc = await transactions_collection.find_one({"_id": oid})
    if not doc:
        return None
    return _serialize_transaction(doc)
 
 
async def delete_transaction(transaction_id: str) -> bool:
    oid = _parse_object_id(transaction_id)
    result = await transactions_collection.delete_one({"_id": oid})
    return result.deleted_count > 0