from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)

from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


# Get all categories
@router.get("/", response_model=list[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CategoryService(db)

    return await service.get_all_categories(current_user.id)


# Get category by ID
@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CategoryService(db)

    return await service.get_category_by_id(category_id, current_user.id)


# Create category
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=201,
)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CategoryService(db)

    return await service.create_category(category_data, current_user.id)


# Update category (PUT - partial update supported)
@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CategoryService(db)

    return await service.update_category(category_id, current_user.id, category_data)


# Delete category (soft delete)
@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CategoryService(db)

    await service.delete_category(category_id, current_user.id)

    return {"message": "Category deleted successfully"}
