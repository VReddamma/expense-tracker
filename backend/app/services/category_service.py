from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.core.exceptions import NotFoundException, ConflictException


class CategoryService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_repo = CategoryRepository(db)

    # Get all categories for a user
    async def get_all_categories(self, user_id: str):
        return await self.category_repo.get_all_by_user(user_id)

    # Get category by ID
    async def get_category_by_id(self, category_id: str, user_id: str):
        category = await self.category_repo.get_by_id(category_id, user_id)

        if not category:
            raise NotFoundException("Category not found")

        return category

    # Create category
    async def create_category(self, category_data: CategoryCreate, user_id: str):
        result = await self.db.execute(
            select(Category).where(
                Category.user_id == user_id,
                Category.name == category_data.name,
                Category.is_active == True,
            )
        )

        existing_category = result.scalar_one_or_none()

        if existing_category:
            raise ConflictException("Category already exists")

        try:
            category = await self.category_repo.create(category_data, user_id)

            await self.db.commit()
            return category

        except Exception:
            await self.db.rollback()
            raise

    # Update category
    async def update_category(
        self, category_id: str, user_id: str, category_data: CategoryUpdate
    ):
        category = await self.get_category_by_id(category_id, user_id)

        update_data = category_data.model_dump(exclude_unset=True)

        if "name" in update_data:
            result = await self.db.execute(
                select(Category).where(
                    Category.user_id == user_id,
                    Category.name == update_data["name"],
                    Category.id != category_id,
                    Category.is_active == True,
                )
            )

            if result.scalar_one_or_none():
                raise ConflictException("Category name already exists")

        try:
            updated_category = await self.category_repo.update(category, category_data)

            await self.db.commit()
            return updated_category

        except Exception:
            await self.db.rollback()
            raise

    # Delete category
    async def delete_category(self, category_id: str, user_id: str):
        category = await self.get_category_by_id(category_id, user_id)

        try:
            await self.category_repo.delete(category)
            await self.db.commit()
            return True

        except Exception:
            await self.db.rollback()
            raise
