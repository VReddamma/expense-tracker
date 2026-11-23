from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.budget_repository import BudgetRepository
from app.schemas.budget import BudgetCreate, BudgetUpdate
from app.core.exceptions import (
    NotFoundException,
    BadRequestException,
    ConflictException,
)


class BudgetService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.budget_repo = BudgetRepository(db)

    # Get all budgets for a user
    async def get_all_budgets(self, user_id: str):
        return await self.budget_repo.get_all_by_user(user_id)

    # Get budget by ID
    async def get_budget_by_id(self, budget_id: str, user_id: str):
        budget = await self.budget_repo.get_by_id(budget_id, user_id)

        if not budget:
            raise NotFoundException("Budget not found")

        return budget

    # Get budgets for a particular month and year
    async def get_monthly_budgets(self, user_id: str, month: int, year: int):

        if month < 1 or month > 12:
            raise BadRequestException("Month must be between 1 and 12")

        if year < 2000:
            raise BadRequestException("Year must be 2000 or later")

        return await self.budget_repo.get_by_month_year(user_id, month, year)

    # Validate category
    async def validate_category(self, category_id: str | None, user_id: str):

        if category_id is None:
            return

        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id,
                Category.user_id == user_id,
                Category.type == "expense",
                Category.is_active == True,
            )
        )

        category = result.scalar_one_or_none()

        if not category:
            raise BadRequestException("Invalid expense category")

    # Create budget
    async def create_budget(self, budget_data: BudgetCreate, user_id: str):

        await self.validate_category(budget_data.category_id, user_id)

        existing_budgets = await self.budget_repo.get_by_month_year(
            user_id, budget_data.month, budget_data.year
        )

        for budget in existing_budgets:
            if budget.category_id == budget_data.category_id:
                raise ConflictException(
                    "Budget already exists for this category and month"
                )

        try:
            budget = await self.budget_repo.create(budget_data, user_id)

            await self.db.commit()
            return budget

        except Exception:
            await self.db.rollback()
            raise

    # Update budget
    async def update_budget(
        self, budget_id: str, user_id: str, budget_data: BudgetUpdate
    ):
        budget = await self.get_budget_by_id(budget_id, user_id)

        update_data = budget_data.model_dump(exclude_unset=True)

        if not update_data:
            raise BadRequestException("No fields provided for update")

        # Get the final category, month and year
        category_id = update_data.get("category_id", budget.category_id)

        month = update_data.get("month", budget.month)
        year = update_data.get("year", budget.year)

        await self.validate_category(category_id, user_id)

        existing_budget = await self.budget_repo.get_existing_budget(
            user_id=user_id,
            category_id=category_id,
            month=month,
            year=year,
            exclude_budget_id=budget_id,
        )

        if existing_budget:
            raise ConflictException("Budget already exists for this category and month")

        try:
            updated_budget = await self.budget_repo.update(budget, budget_data)

            await self.db.commit()
            return updated_budget

        except Exception:
            await self.db.rollback()
            raise

    # Delete budget
    async def delete_budget(self, budget_id: str, user_id: str):

        budget = await self.get_budget_by_id(budget_id, user_id)

        try:
            await self.budget_repo.delete(budget)
            await self.db.commit()
            return True

        except Exception:
            await self.db.rollback()
            raise
