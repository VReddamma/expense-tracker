from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetUpdate


class BudgetRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Get all budgets belonging to a user
    async def get_all_by_user(self, user_id: str):
        result = await self.db.execute(select(Budget).where(Budget.user_id == user_id))

        return result.scalars().all()

    # Get one budget by ID
    async def get_by_id(self, budget_id: str, user_id: str):
        result = await self.db.execute(
            select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        )

        return result.scalar_one_or_none()

    # Get budgets for a particular month and year
    async def get_by_month_year(self, user_id: str, month: int, year: int):
        result = await self.db.execute(
            select(Budget).where(
                Budget.user_id == user_id, Budget.month == month, Budget.year == year
            )
        )

        return result.scalars().all()

    # Create a new budget
    async def create(self, budget_data: BudgetCreate, user_id: str):
        new_budget = Budget(
            user_id=user_id,
            category_id=budget_data.category_id,
            amount=budget_data.amount,
            month=budget_data.month,
            year=budget_data.year,
        )

        self.db.add(new_budget)

        await self.db.flush()
        await self.db.refresh(new_budget)

        return new_budget

    # Update an existing budget
    async def update(self, budget: Budget, budget_data: BudgetUpdate):
        update_data = budget_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(budget, field, value)

        await self.db.flush()
        await self.db.refresh(budget)

        return budget

    # Delete a budget
    async def delete(self, budget: Budget):
        await self.db.delete(budget)
        await self.db.flush()

        return True

    # Get Existing Budget
    async def get_existing_budget(
        self,
        user_id: str,
        category_id: str | None,
        month: int,
        year: int,
        exclude_budget_id: str | None = None,
    ):
        query = select(Budget).where(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.month == month,
            Budget.year == year,
        )

        if exclude_budget_id:
            query = query.where(Budget.id != exclude_budget_id)

        result = await self.db.execute(query)

        return result.scalar_one_or_none()
