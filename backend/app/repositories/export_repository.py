from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.models.category import Category


class ExportRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Get transactions for export
    async def get_transactions(
        self,
        user_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ):

        query = (
            select(
                Transaction.id,
                Transaction.title,
                Category.name.label("category_name"),
                Transaction.type,
                Transaction.amount,
                Transaction.transaction_date,
                Transaction.payment_method,
                Transaction.notes,
            )
            .outerjoin(Category, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id)
        )

        # Apply start date filter
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)

        # Apply end date filter
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)

        # Latest transactions first
        query = query.order_by(
            Transaction.transaction_date.desc(), Transaction.created_at.desc()
        )

        result = await self.db.execute(query)

        return result.mappings().all()
