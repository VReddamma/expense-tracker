from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.dashboard import (
    DashboardSummary,
    MonthlyTrend,
    CategoryBreakdown,
    RecentTransaction,
)

from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# Dashboard summary
@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DashboardService(db)

    return await service.get_summary(current_user.id, month, year)


# Monthly income and expense trends
@router.get("/monthly-trends", response_model=list[MonthlyTrend])
async def get_monthly_trends(
    year: int = Query(ge=2000),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DashboardService(db)

    return await service.get_monthly_trends(current_user.id, year)


# Expense category breakdown
@router.get(
    "/category-breakdown",
    response_model=list[CategoryBreakdown],
)
async def get_category_breakdown(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DashboardService(db)

    return await service.get_category_breakdown(current_user.id, month, year)


# Recent transactions
@router.get(
    "/recent-transactions",
    response_model=list[RecentTransaction],
)
async def get_recent_transactions(
    limit: int = Query(default=5, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DashboardService(db)

    return await service.get_recent_transactions(current_user.id, limit)
