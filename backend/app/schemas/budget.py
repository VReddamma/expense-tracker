from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# Create budget request
class BudgetCreate(BaseModel):

    category_id: str | None = None

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    month: int = Field(ge=1, le=12)

    year: int = Field(ge=2000, le=2100)


# Update budget request
class BudgetUpdate(BaseModel):

    category_id: str | None = None

    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)

    month: int | None = Field(default=None, ge=1, le=12)

    year: int | None = Field(default=None, ge=2000, le=2100)

    model_config = ConfigDict(extra="forbid")


# Budget response
class BudgetResponse(BaseModel):

    id: str
    user_id: str
    category_id: str | None
    amount: Decimal
    month: int
    year: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
