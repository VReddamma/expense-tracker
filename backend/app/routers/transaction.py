from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
)

from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


# Get all transactions with filters and pagination
@router.get("/")
async def get_transactions(
    transaction_type: str | None = Query(default=None, alias="type"),
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: str | None = None,
    search: str | None = None,
    sort_by: str = "transaction_date",
    sort_order: str = "desc",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TransactionService(db)

    return await service.get_all_transactions(
        user_id=current_user.id,
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
@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TransactionService(db)

    return await service.get_transaction_by_id(transaction_id, current_user.id)


# Create transaction
@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=201,
)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TransactionService(db)

    return await service.create_transaction(transaction_data, current_user.id)


# Update transaction
@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TransactionService(db)

    return await service.update_transaction(
        transaction_id,
        current_user.id,
        transaction_data,
    )


# Delete transaction
@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TransactionService(db)

    await service.delete_transaction(transaction_id, current_user.id)

    return {"message": "Transaction deleted successfully"}
