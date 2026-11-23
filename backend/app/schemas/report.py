from datetime import date

from pydantic import BaseModel, ConfigDict


class ReportSummary(BaseModel):
    total_income: float
    total_expenses: float
    balance: float


class MonthlyReport(ReportSummary):
    month: int
    year: int


class MonthlyReportItem(BaseModel):
    month: int
    income: float
    expenses: float
    balance: float


class YearlyReport(ReportSummary):
    year: int
    monthly_data: list[MonthlyReportItem]


class CategoryReportItem(BaseModel):
    category_id: str | None
    category_name: str
    total_amount: float
    transaction_count: int


class PaymentMethodReportItem(BaseModel):
    payment_method: str
    total_amount: float
    transaction_count: int


class CustomDateReport(ReportSummary):
    start_date: date
    end_date: date
