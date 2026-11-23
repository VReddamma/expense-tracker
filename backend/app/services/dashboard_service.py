from decimal import Decimal

from sqlalchemy import select, func, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.models.category import Category
from app.core.exceptions import BadRequestException


class DashboardService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Validate month and year
    def validate_month_year(self, month: int, year: int):
        if month < 1 or month > 12:
            raise BadRequestException("Month must be between 1 and 12")

        if year < 2000:
            raise BadRequestException("Year must be 2000 or later")

    # Get income, expenses, savings and savings rate
    async def get_summary(self, user_id: str, month: int, year: int):

        self.validate_month_year(month, year)

        income_expression = func.coalesce(
            func.sum(case((Transaction.type == "income", Transaction.amount), else_=0)),
            0,
        )

        expense_expression = func.coalesce(
            func.sum(
                case((Transaction.type == "expense", Transaction.amount), else_=0)
            ),
            0,
        )

        result = await self.db.execute(
            select(
                income_expression.label("total_income"),
                expense_expression.label("total_expenses"),
            ).where(
                Transaction.user_id == user_id,
                extract("month", Transaction.transaction_date) == month,
                extract("year", Transaction.transaction_date) == year,
            )
        )

        row = result.one()

        total_income = Decimal(str(row.total_income))
        total_expenses = Decimal(str(row.total_expenses))
        net_savings = total_income - total_expenses

        savings_rate = (
            (net_savings / total_income) * Decimal("100")
            if total_income > 0
            else Decimal("0")
        )

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_savings": net_savings,
            "savings_rate": savings_rate,
        }

    # Get monthly income and expense trends for a year
    async def get_monthly_trends(self, user_id: str, year: int):

        if year < 2000:
            raise BadRequestException("Year must be 2000 or later")

        income_expression = func.coalesce(
            func.sum(case((Transaction.type == "income", Transaction.amount), else_=0)),
            0,
        )

        expense_expression = func.coalesce(
            func.sum(
                case((Transaction.type == "expense", Transaction.amount), else_=0)
            ),
            0,
        )

        result = await self.db.execute(
            select(
                extract("month", Transaction.transaction_date).label("month"),
                income_expression.label("income"),
                expense_expression.label("expenses"),
            )
            .where(
                Transaction.user_id == user_id,
                extract("year", Transaction.transaction_date) == year,
            )
            .group_by(
                extract("year", Transaction.transaction_date),
                extract("month", Transaction.transaction_date),
            )
            .order_by(extract("month", Transaction.transaction_date))
        )

        monthly_data = {}

        for row in result.all():
            income = Decimal(str(row.income))
            expenses = Decimal(str(row.expenses))

            monthly_data[int(row.month)] = {
                "income": income,
                "expenses": expenses,
            }

        trends = []

        for month in range(1, 13):

            data = monthly_data.get(
                month,
                {
                    "income": Decimal("0.00"),
                    "expenses": Decimal("0.00"),
                },
            )

            income = data["income"]
            expenses = data["expenses"]

            trends.append(
                {
                    "month": month,
                    "year": year,
                    "income": income,
                    "expenses": expenses,
                    "savings": income - expenses,
                }
            )

        return trends

    # Get expense breakdown by category for a month
    async def get_category_breakdown(self, user_id: str, month: int, year: int):

        self.validate_month_year(month, year)

        result = await self.db.execute(
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                func.sum(Transaction.amount).label("total_amount"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                extract("month", Transaction.transaction_date) == month,
                extract("year", Transaction.transaction_date) == year,
            )
            .group_by(Category.id, Category.name)
            .order_by(func.sum(Transaction.amount).desc())
        )

        rows = result.all()

        total_expenses = sum(
            (Decimal(str(row.total_amount)) for row in rows), Decimal("0")
        )

        breakdown = []

        for row in rows:
            amount = Decimal(str(row.total_amount))

            percentage = (
                (amount / total_expenses) * Decimal("100")
                if total_expenses > 0
                else Decimal("0")
            )

            breakdown.append(
                {
                    "category_id": row.category_id,
                    "category_name": row.category_name,
                    "total_amount": amount,
                    "percentage": percentage,
                }
            )

        return breakdown

    # Get latest transactions
    async def get_recent_transactions(self, user_id: str, limit: int = 5):

        if limit < 1 or limit > 100:
            raise BadRequestException("Limit must be between 1 and 100")

        result = await self.db.execute(
            select(
                Transaction.id,
                Transaction.title,
                Transaction.amount,
                Transaction.type,
                Transaction.transaction_date,
                Category.name.label("category_name"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id)
            .order_by(
                Transaction.transaction_date.desc(), Transaction.created_at.desc()
            )
            .limit(limit)
        )

        return [
            {
                "id": row.id,
                "title": row.title,
                "amount": row.amount,
                "type": row.type,
                "transaction_date": row.transaction_date,
                "category_name": row.category_name,
            }
            for row in result.all()
        ]
