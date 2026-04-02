from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

from app.schemas.transaction_schema import TransactionCreate, TransactionOut, TransactionUpdate
from app.services.transaction_service import (
    create_transaction as create_transaction_service,
    delete_transaction as delete_transaction_service,
    get_transaction_by_id,
    list_transactions as list_transactions_service,
    update_transaction as update_transaction_service,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _serialize_transaction(doc: dict) -> dict:
    doc = doc.copy()
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.post("/", response_model=TransactionOut)
async def create_transaction(data: TransactionCreate):
    doc = data.model_dump(exclude_none=True)
    created = await create_transaction_service(doc)
    return created


@router.get("/", response_model=List[TransactionOut])
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_flagged: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
):
    docs = await list_transactions_service(
        skip=skip,
        limit=limit,
        is_flagged=is_flagged,
        min_amount=min_amount,
        max_amount=max_amount,
    )
    return docs


@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction(transaction_id: str):
    try:
        oid = ObjectId(transaction_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid transaction_id") from e

    doc = await get_transaction_by_id(str(oid))
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return doc


@router.put("/{transaction_id}", response_model=TransactionOut)
async def update_transaction(transaction_id: str, data: TransactionUpdate):
    try:
        oid = ObjectId(transaction_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid transaction_id") from e

    update_doc = data.model_dump(exclude_none=True)
    if not update_doc:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    doc = await update_transaction_service(str(oid), update_doc)
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return doc


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str):
    try:
        oid = ObjectId(transaction_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid transaction_id") from e

    deleted = await delete_transaction_service(str(oid))
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"deleted": True, "transaction_id": transaction_id}