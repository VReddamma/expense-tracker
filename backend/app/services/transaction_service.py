from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ConflictException,
)


class TransactionService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.transaction_repo = TransactionRepository(db)

    # Get transactions with filtering and pagination
    async def get_all_transactions(
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
        if page < 1 or limit < 1 or limit > 100:
            raise BadRequestException("Invalid pagination values")

        if start_date and end_date and start_date > end_date:
            raise BadRequestException("Start date cannot be after end date")

        return await self.transaction_repo.get_all_by_user(
            user_id=user_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit,
        )

    # Get transaction by ID
    async def get_transaction_by_id(self, transaction_id: str, user_id: str):
        transaction = await self.transaction_repo.get_by_id(transaction_id, user_id)

        if not transaction:
            raise NotFoundException("Transaction not found")

        return transaction

    # Validate category ownership and transaction type
    async def validate_category(
        self, category_id: str, user_id: str, transaction_type: str
    ):
        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id,
                Category.user_id == user_id,
                Category.is_active == True,
            )
        )

        category = result.scalar_one_or_none()

        if not category:
            raise NotFoundException("Category not found or inactive")

        if category.type != transaction_type:
            raise BadRequestException("Category type does not match transaction type")

        return category

    # Create transaction
    async def create_transaction(
        self, transaction_data: TransactionCreate, user_id: str
    ):
        await self.validate_category(
            transaction_data.category_id, user_id, transaction_data.type
        )

        try:
            transaction = await self.transaction_repo.create(transaction_data, user_id)

            await self.db.commit()
            return transaction

        except Exception:
            await self.db.rollback()
            raise

    # Update transaction
    async def update_transaction(
        self, transaction_id: str, user_id: str, transaction_data: TransactionUpdate
    ):
        transaction = await self.get_transaction_by_id(transaction_id, user_id)

        update_data = transaction_data.model_dump(exclude_unset=True)

        # Check whether any fields were provided
        if not update_data:
            raise BadRequestException("No fields provided for update")

        # These fields cannot be NULL
        required_fields = {"category_id", "title", "amount", "type", "transaction_date"}

        for field in required_fields:
            if field in update_data and update_data[field] is None:
                raise BadRequestException(f"{field} cannot be null")

        # Get the final category and transaction type
        category_id = update_data.get("category_id", transaction.category_id)

        transaction_type = update_data.get("type", transaction.type)

        # Validate category ownership and type
        await self.validate_category(category_id, user_id, transaction_type)

        try:
            updated_transaction = await self.transaction_repo.update(
                transaction, transaction_data
            )

            await self.db.commit()

            return updated_transaction

        except Exception:
            await self.db.rollback()
            raise

    # Delete transaction
    async def delete_transaction(self, transaction_id: str, user_id: str):
        transaction = await self.get_transaction_by_id(transaction_id, user_id)

        try:
            await self.transaction_repo.delete(transaction)
            await self.db.commit()
            return True

        except Exception:
            await self.db.rollback()
            raise
