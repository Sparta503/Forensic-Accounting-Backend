from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from io import StringIO
import csv

from app.schemas.transaction_schema import TransactionCreate, TransactionOut, TransactionUpdate
from app.services.transaction_service import (
    create_transaction as create_transaction_service,
    delete_transaction as delete_transaction_service,
    get_transaction_by_id,
    bulk_import_transactions,
    list_transactions as list_transactions_service,
    update_transaction as update_transaction_service,
)

from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


# ===============================
# CREATE
# ===============================
@router.post("/", response_model=TransactionOut)
async def create_transaction(
    data: TransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    doc = data.model_dump(exclude_none=True, by_alias=True)

    # IMPORTANT: force ownership from JWT
    created = await create_transaction_service(
        doc,
        current_user["user_id"]
    )

    return created


# ===============================
# IMPORT CSV
# ===============================
@router.post("/import-csv")
async def import_transactions_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from e

    reader = csv.DictReader(StringIO(text))
    required_headers = [
        "Date",
        "Mode",
        "Category",
        "Subcategory",
        "Note",
        "Amount",
        "Income/Expense",
        "Currency",
    ]

    if reader.fieldnames is None:
        raise HTTPException(status_code=400, detail="CSV is missing headers")

    missing = [h for h in required_headers if h not in reader.fieldnames]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"CSV headers missing: {', '.join(missing)}",
        )

    inserted = 0
    failed: List[dict] = []

    for row_index, row in enumerate(reader, start=2):
        try:
            if row.get("Amount") is None or str(row.get("Amount")).strip() == "":
                raise ValueError("Amount is required")

            amount_raw = str(row["Amount"]).replace(",", "").strip()
            row["Amount"] = float(amount_raw)

            payload = TransactionCreate.model_validate(row)
            doc = payload.model_dump(exclude_none=True, by_alias=True)

            await create_transaction_service(doc, current_user["user_id"])
            inserted += 1
        except Exception as e:
            failed.append({"row": row_index, "error": str(e)})

    return {
        "inserted": inserted,
        "failed": failed,
        "total": inserted + len(failed),
    }


# ===============================
# IMPORT CSV FAST
# ===============================
@router.post("/import-csv-fast")
async def import_transactions_csv_fast(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from e

    reader = csv.DictReader(StringIO(text))
    required_headers = [
        "Date",
        "Mode",
        "Category",
        "Subcategory",
        "Note",
        "Amount",
        "Income/Expense",
        "Currency",
    ]

    if reader.fieldnames is None:
        raise HTTPException(status_code=400, detail="CSV is missing headers")

    missing = [h for h in required_headers if h not in reader.fieldnames]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"CSV headers missing: {', '.join(missing)}",
        )

    docs = []
    failed: List[dict] = []

    for row_index, row in enumerate(reader, start=2):
        try:
            if row.get("Amount") is None or str(row.get("Amount")).strip() == "":
                raise ValueError("Amount is required")

            amount_raw = str(row["Amount"]).replace(",", "").strip()
            row["Amount"] = float(amount_raw)

            payload = TransactionCreate.model_validate(row)
            doc = payload.model_dump(exclude_none=True, by_alias=True)
            docs.append(doc)
        except Exception as e:
            failed.append({"row": row_index, "error": str(e)})

    result = await bulk_import_transactions(docs, current_user["user_id"])
    return {
        "inserted": result["inserted"],
        "batches": result["batches"],
        "failed": failed,
        "total": result["inserted"] + len(failed),
        "note": "Fast import bypasses per-row fraud detection and audit logs. Use /import-csv for full pipeline.",
    }


# ===============================
# LIST
# ===============================
@router.get("/", response_model=List[TransactionOut])
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_flagged: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    current_user: dict = Depends(get_current_user)
):
    return await list_transactions_service(
        skip=skip,
        limit=limit,
        is_flagged=is_flagged,
        min_amount=min_amount,
        max_amount=max_amount,
        user_id=None
    )


# ===============================
# GET BY ID
# ===============================
@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    doc = await get_transaction_by_id(transaction_id, None)

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return doc


# ===============================
# UPDATE
# ===============================
@router.put("/{transaction_id}", response_model=TransactionOut)
async def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    current_user: dict = Depends(get_current_user)
):
    update_doc = data.model_dump(exclude_none=True, by_alias=True)

    if not update_doc:
        raise HTTPException(
            status_code=400,
            detail="No fields provided to update"
        )

    doc = await update_transaction_service(
        transaction_id,
        update_doc,
        current_user["user_id"]
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found or not owned by user"
        )

    return doc


# ===============================
# DELETE
# ===============================
@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user)
):
    deleted = await delete_transaction_service(
        transaction_id,
        current_user["user_id"]
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found or not owned by user"
        )

    return {
        "deleted": True,
        "transaction_id": transaction_id
    }