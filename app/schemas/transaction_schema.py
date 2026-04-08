from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class TransactionCreate(BaseModel):
    # user_id will be auto-filled from JWT, not provided by client
    user_id: Optional[str] = Field(None, example="Automatically assigned from JWT")
    amount: float = Field(..., example=120.5)
    description: Optional[str] = Field(None, example="Payment for groceries")
    currency: Optional[str] = Field(None, example="USD")
    transaction_date: Optional[datetime] = Field(None, example="2026-04-08T23:06:54.452Z")
    merchant: Optional[str] = Field(None, example="Walmart")
    category: Optional[str] = Field(None, example="Groceries")
    from_account: Optional[str] = Field(None, example="Checking Account")
    to_account: Optional[str] = Field(None, example="Merchant Account")
    location: Optional[str] = Field(None, example="New York")
    is_flagged: bool = Field(False, example=False)
    metadata: Optional[Dict[str, Any]] = Field(None, example={"notes": "Weekly groceries"})

    class Config:
        schema_extra = {
            "example": {
                "amount": 120.5,
                "description": "Payment for groceries",
                "currency": "USD",
                "transaction_date": "2026-04-08T23:06:54.452Z",
                "merchant": "Walmart",
                "category": "Groceries",
                "from_account": "Checking Account",
                "to_account": "Merchant Account",
                "location": "New York",
                "is_flagged": False,
                "metadata": {"notes": "Weekly groceries"},
                "user_id": "Automatically assigned from JWT"
            }
        }


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    transaction_date: Optional[datetime] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    location: Optional[str] = None
    is_flagged: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id", example="643e5b8d2f3b2a1f4c8b4567")
    user_id: Optional[str] = Field(None, example="643e5b8d2f3b2a1f4c8b1234")
    amount: float = Field(..., example=120.5)
    description: Optional[str] = Field(None, example="Payment for groceries")
    currency: Optional[str] = Field(None, example="USD")
    transaction_date: Optional[datetime] = Field(None, example="2026-04-08T23:06:54.452Z")
    merchant: Optional[str] = Field(None, example="Walmart")
    category: Optional[str] = Field(None, example="Groceries")
    from_account: Optional[str] = Field(None, example="Checking Account")
    to_account: Optional[str] = Field(None, example="Merchant Account")
    location: Optional[str] = Field(None, example="New York")
    is_flagged: bool = Field(False, example=False)
    is_fraud: Optional[bool] = Field(None, example=False)
    risk_score: Optional[int] = Field(None, example=15)
    fraud_reasons: Optional[List[str]] = Field(None, example=["High-risk merchant"])
    timestamp: Optional[datetime] = Field(None, example="2026-04-08T23:07:00.000Z")
    metadata: Optional[Dict[str, Any]] = Field(None, example={"notes": "Weekly groceries"})