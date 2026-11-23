from datetime import date

from sqlalchemy import select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Get transactions with filtering and pagination

    async def get_all_by_user(
        self,
        user_id: str,
        transaction_type: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        category_id: str | None = None,
        search: str | None = None,
        sort_by: str = "transaction_date",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 10,
    ):
        # Base query
        query = select(Transaction).where(Transaction.user_id == user_id)

        # Filter by income or expense
        if transaction_type:
            query = query.where(Transaction.type == transaction_type)

        # Filter by date range
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)

        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)

        # Filter by category
        if category_id:
            query = query.where(Transaction.category_id == category_id)

        # Search by transaction title
        if search:
            query = query.where(Transaction.title.ilike(f"%{search}%"))

        # Get total matching records BEFORE pagination
        count_query = select(func.count()).select_from(query.subquery())

        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()

        # Sorting
        sort_columns = {
            "transaction_date": Transaction.transaction_date,
            "amount": Transaction.amount,
            "created_at": Transaction.created_at,
            "title": Transaction.title,
        }

        sort_column = sort_columns.get(sort_by, Transaction.transaction_date)

        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        # Pagination
        offset = (page - 1) * limit

        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)

        items = result.scalars().all()

        return {"items": items, "total": total, "page": page, "limit": limit}

    # Get one transaction by ID
    async def get_by_id(self, transaction_id: str, user_id: str):
        result = await self.db.execute(
            select(Transaction).where(
                Transaction.id == transaction_id, Transaction.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    # Create a transaction
    async def create(self, transaction_data: TransactionCreate, user_id: str):
        new_transaction = Transaction(
            user_id=user_id,
            category_id=transaction_data.category_id,
            title=transaction_data.title,
            amount=transaction_data.amount,
            type=transaction_data.type,
            transaction_date=transaction_data.transaction_date,
            payment_method=transaction_data.payment_method,
            notes=transaction_data.notes,
        )

        self.db.add(new_transaction)

        await self.db.flush()
        await self.db.refresh(new_transaction)

        return new_transaction

    # Update a transaction
    async def update(
        self, transaction: Transaction, transaction_data: TransactionUpdate
    ):
        update_data = transaction_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(transaction, field, value)

        await self.db.flush()
        await self.db.refresh(transaction)

        return transaction

    # Delete a transaction
    async def delete(self, transaction: Transaction):
        await self.db.delete(transaction)
        await self.db.flush()

        return True
