from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Depends

from app.schemas.transaction_schema import TransactionCreate, TransactionOut, TransactionUpdate
from app.services.transaction_service import (
    create_transaction as create_transaction_service,
    delete_transaction as delete_transaction_service,
    get_transaction_by_id,
    list_transactions as list_transactions_service,
    update_transaction as update_transaction_service,
)
from app.utils.dependencies import get_current_user  # JWT extraction

router = APIRouter(prefix="/transactions", tags=["transactions"])


# -------------------------------
# CREATE TRANSACTION
# -------------------------------
@router.post("/", response_model=TransactionOut)
async def create_transaction(
    data: TransactionCreate,
    current_user: dict = Depends(get_current_user)  # inject user from JWT
):
    doc = data.model_dump(exclude_none=True)
    doc["user_id"] = current_user["user_id"]  # assign logged-in user
    created = await create_transaction_service(doc)
    return created


# -------------------------------
# LIST TRANSACTIONS (with filters)
# -------------------------------
@router.get("/", response_model=List[TransactionOut])
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_flagged: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    current_user: dict = Depends(get_current_user)  # secure: only their transactions
):
    docs = await list_transactions_service(
        skip=skip,
        limit=limit,
        is_flagged=is_flagged,
        min_amount=min_amount,
        max_amount=max_amount,
        user_id=current_user["user_id"],  # filter by user
    )
    return docs


# -------------------------------
# GET TRANSACTION BY ID
# -------------------------------
@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        oid = ObjectId(transaction_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid transaction_id") from e

    doc = await get_transaction_by_id(str(oid))
    if not doc or doc["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return doc


# -------------------------------
# UPDATE TRANSACTION
# -------------------------------
@router.put("/{transaction_id}", response_model=TransactionOut)
async def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        oid = ObjectId(transaction_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid transaction_id") from e

    update_doc = data.model_dump(exclude_none=True)
    if not update_doc:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    doc = await update_transaction_service(str(oid), update_doc, current_user["user_id"])
    if not doc:
        raise HTTPException(status_code=404, detail="Transaction not found or not owned by user")
    return doc


# -------------------------------
# DELETE TRANSACTION
# -------------------------------
@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        oid = ObjectId(transaction_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid transaction_id") from e

    deleted = await delete_transaction_service(str(oid), current_user["user_id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found or not owned by user")
    return {"deleted": True, "transaction_id": transaction_id}