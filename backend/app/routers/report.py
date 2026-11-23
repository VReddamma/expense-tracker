from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.report import (
    MonthlyReport,
    YearlyReport,
    CategoryReportItem,
    PaymentMethodReportItem,
    CustomDateReport,
)

from app.services.report_service import ReportService

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# Monthly financial report
@router.get("/monthly", response_model=MonthlyReport)
async def get_monthly_report(
    month: int,
    year: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)

    return await service.get_monthly_report(current_user.id, month, year)


# Yearly financial report
@router.get("/yearly", response_model=YearlyReport)
async def get_yearly_report(
    year: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)

    return await service.get_yearly_report(current_user.id, year)


# Income report
@router.get("/income", response_model=list[CategoryReportItem])
async def get_income_report(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)

    return await service.get_income_report(current_user.id, start_date, end_date)


# Expense report
@router.get("/expenses", response_model=list[CategoryReportItem])
async def get_expense_report(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)

    return await service.get_expense_report(current_user.id, start_date, end_date)


# Category-wise spending report
@router.get("/categories", response_model=list[CategoryReportItem])
async def get_category_report(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)

    return await service.get_category_report(current_user.id, start_date, end_date)


# Payment method report
@router.get(
    "/payment-methods",
    response_model=list[PaymentMethodReportItem],
)
async def get_payment_method_report(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)

    return await service.get_payment_method_report(
        current_user.id, start_date, end_date
    )


# Custom date-range report
@router.get("/custom", response_model=CustomDateReport)
async def get_custom_report(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)

    return await service.get_custom_report(current_user.id, start_date, end_date)
