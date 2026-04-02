from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    currency: Optional[str] = None
    transaction_date: Optional[datetime] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    is_flagged: bool = False
    metadata: Optional[Dict[str, Any]] = None


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    transaction_date: Optional[datetime] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    is_flagged: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    amount: float
    description: Optional[str] = None
    currency: Optional[str] = None
    transaction_date: Optional[datetime] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    is_flagged: bool = False
    metadata: Optional[Dict[str, Any]] = None