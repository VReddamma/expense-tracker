from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

PaymentMethod = Literal[
    "cash", "upi", "credit_card", "debit_card", "bank_transfer", "other"
]


# Create transaction request
class TransactionCreate(BaseModel):

    category_id: str

    title: str = Field(min_length=2, max_length=150)

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    type: Literal["income", "expense"]

    transaction_date: date

    payment_method: PaymentMethod | None = None

    notes: str | None = None


# Update transaction request
class TransactionUpdate(BaseModel):

    category_id: str | None = None

    title: str | None = Field(default=None, min_length=2, max_length=150)

    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)

    type: Literal["income", "expense"] | None = None

    transaction_date: date | None = None

    payment_method: PaymentMethod | None = None

    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


# Transaction response
class TransactionResponse(BaseModel):

    id: str
    user_id: str
    category_id: str
    title: str
    amount: Decimal
    type: Literal["income", "expense"]
    transaction_date: date
    payment_method: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
