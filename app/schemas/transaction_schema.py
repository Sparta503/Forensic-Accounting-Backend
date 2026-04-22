from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(alias="Date")
    mode: Optional[str] = Field(default=None, alias="Mode")
    category: Optional[str] = Field(default=None, alias="Category")
    subcategory: Optional[str] = Field(default=None, alias="Subcategory")
    note: Optional[str] = Field(default=None, alias="Note")
    amount: float = Field(alias="Amount")
    income_expense: Optional[str] = Field(default=None, alias="Income/Expense")
    currency: Optional[str] = Field(default=None, alias="Currency")

    user_id: Optional[str] = None
    is_flagged: bool = False
    metadata: Optional[Dict[str, Any]] = None


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: Optional[str] = Field(default=None, alias="Date")
    mode: Optional[str] = Field(default=None, alias="Mode")
    category: Optional[str] = Field(default=None, alias="Category")
    subcategory: Optional[str] = Field(default=None, alias="Subcategory")
    note: Optional[str] = Field(default=None, alias="Note")
    amount: Optional[float] = Field(default=None, alias="Amount")
    income_expense: Optional[str] = Field(default=None, alias="Income/Expense")
    currency: Optional[str] = Field(default=None, alias="Currency")

    is_flagged: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id", example="643e5b8d2f3b2a1f4c8b4567")

    date: str = Field(alias="Date")
    mode: Optional[str] = Field(default=None, alias="Mode")
    category: Optional[str] = Field(default=None, alias="Category")
    subcategory: Optional[str] = Field(default=None, alias="Subcategory")
    note: Optional[str] = Field(default=None, alias="Note")
    amount: float = Field(alias="Amount")
    income_expense: Optional[str] = Field(default=None, alias="Income/Expense")
    currency: Optional[str] = Field(default=None, alias="Currency")

    user_id: Optional[str] = None
    is_flagged: bool = False
    is_fraud: Optional[bool] = Field(None, example=False)
    risk_score: Optional[int] = Field(None, example=15)
    fraud_reasons: Optional[List[str]] = Field(None, example=["High-risk merchant"])
    timestamp: Optional[datetime] = Field(None, example="2026-04-08T23:07:00.000Z")
    metadata: Optional[Dict[str, Any]] = Field(None, example={"notes": "Weekly groceries"})