from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
)

from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


# Get all budgets
@router.get("/", response_model=list[BudgetResponse])
async def get_budgets(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BudgetService(db)

    return await service.get_all_budgets(current_user.id)


# Get budgets by month and year
@router.get("/monthly", response_model=list[BudgetResponse])
async def get_monthly_budgets(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BudgetService(db)

    return await service.get_monthly_budgets(current_user.id, month, year)


# Get budget by ID
@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BudgetService(db)

    return await service.get_budget_by_id(budget_id, current_user.id)


# Create budget
@router.post(
    "/",
    response_model=BudgetResponse,
    status_code=201,
)
async def create_budget(
    budget_data: BudgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BudgetService(db)

    return await service.create_budget(budget_data, current_user.id)


# Update budget
@router.patch("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    budget_data: BudgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BudgetService(db)

    return await service.update_budget(
        budget_id,
        current_user.id,
        budget_data,
    )


# Delete budget
@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BudgetService(db)

    await service.delete_budget(budget_id, current_user.id)

    return {"message": "Budget deleted successfully"}
