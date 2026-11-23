from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


# Dashboard summary
class DashboardSummary(BaseModel):

    total_income: Decimal
    total_expenses: Decimal
    net_savings: Decimal
    savings_rate: Decimal


# Monthly income and expense
class MonthlyTrend(BaseModel):

    month: int
    year: int
    income: Decimal
    expenses: Decimal
    savings: Decimal


# Category-wise expense breakdown
class CategoryBreakdown(BaseModel):

    category_id: str
    category_name: str
    total_amount: Decimal
    percentage: Decimal


# Recent transaction
class RecentTransaction(BaseModel):

    id: str
    title: str
    amount: Decimal
    type: str
    transaction_date: date
    category_name: str

    model_config = ConfigDict(from_attributes=True)
