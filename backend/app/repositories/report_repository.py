from datetime import date

from sqlalchemy import select, func, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.models.category import Category


class ReportRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Common financial summary
    async def get_summary(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ):
        income_expr = func.coalesce(
            func.sum(
                case(
                    (Transaction.type == "income", Transaction.amount),
                    else_=0,
                )
            ),
            0,
        )

        expense_expr = func.coalesce(
            func.sum(
                case(
                    (Transaction.type == "expense", Transaction.amount),
                    else_=0,
                )
            ),
            0,
        )

        statement = select(
            income_expr.label("total_income"),
            expense_expr.label("total_expenses"),
        ).where(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
        )

        result = await self.db.execute(statement)
        row = result.one()

        income = float(row.total_income)
        expenses = float(row.total_expenses)

        return {
            "total_income": income,
            "total_expenses": expenses,
            "balance": income - expenses,
        }

    # Yearly monthly aggregation
    async def get_monthly_data(self, user_id: str, year: int):

        income_expr = func.coalesce(
            func.sum(
                case(
                    (Transaction.type == "income", Transaction.amount),
                    else_=0,
                )
            ),
            0,
        )

        expense_expr = func.coalesce(
            func.sum(
                case(
                    (Transaction.type == "expense", Transaction.amount),
                    else_=0,
                )
            ),
            0,
        )

        statement = (
            select(
                extract("month", Transaction.transaction_date).label("month"),
                income_expr.label("income"),
                expense_expr.label("expenses"),
            )
            .where(
                Transaction.user_id == user_id,
                extract("year", Transaction.transaction_date) == year,
            )
            .group_by(extract("month", Transaction.transaction_date))
            .order_by(extract("month", Transaction.transaction_date))
        )

        result = await self.db.execute(statement)
        rows = result.all()

        return [
            {
                "month": int(row.month),
                "income": float(row.income),
                "expenses": float(row.expenses),
                "balance": float(row.income) - float(row.expenses),
            }
            for row in rows
        ]

    # Income or expense grouped by category
    async def get_category_report(
        self,
        user_id: str,
        transaction_type: str,
        start_date: date,
        end_date: date,
    ):

        statement = (
            select(
                Transaction.category_id,
                func.coalesce(Category.name, "Uncategorized").label("category_name"),
                func.sum(Transaction.amount).label("total_amount"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .outerjoin(
                Category,
                Transaction.category_id == Category.id,
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.type == transaction_type,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
            .group_by(
                Transaction.category_id,
                Category.name,
            )
            .order_by(func.sum(Transaction.amount).desc())
        )

        result = await self.db.execute(statement)
        rows = result.all()

        return [
            {
                "category_id": row.category_id,
                "category_name": row.category_name,
                "total_amount": float(row.total_amount),
                "transaction_count": row.transaction_count,
            }
            for row in rows
        ]

    # Payment method breakdown
    async def get_payment_method_report(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ):

        statement = (
            select(
                Transaction.payment_method,
                func.sum(Transaction.amount).label("total_amount"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
            .group_by(Transaction.payment_method)
            .order_by(func.sum(Transaction.amount).desc())
        )

        result = await self.db.execute(statement)
        rows = result.all()

        return [
            {
                "payment_method": row.payment_method,
                "total_amount": float(row.total_amount),
                "transaction_count": row.transaction_count,
            }
            for row in rows
        ]
