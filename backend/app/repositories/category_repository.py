from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Get all categories belonging to a particular user
    async def get_all_by_user(self, user_id: str):
        result = await self.db.execute(
            select(Category).where(
                Category.user_id == user_id, Category.is_active == True
            )
        )

        return result.scalars().all()

    # Get one category by ID and user ID
    async def get_by_id(self, category_id: str, user_id: str):
        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id, Category.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    # Create a new category
    async def create(self, category_data: CategoryCreate, user_id: str):
        new_category = Category(
            user_id=user_id,
            name=category_data.name,
            type=category_data.type,
            color=category_data.color,
            icon=category_data.icon,
        )

        self.db.add(new_category)

        await self.db.flush()
        await self.db.refresh(new_category)

        return new_category

    # Update an existing category
    async def update(self, category: Category, category_data: CategoryUpdate):
        update_data = category_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(category, field, value)

        await self.db.flush()
        await self.db.refresh(category)

        return category

    # Delete a category - Complete Delete
    # async def delete(self, category: Category):
    #     await self.db.delete(category)
    #     await self.db.flush()

    #     return True

    # Instead we are using soft delete
    async def delete(self, category: Category):
        category.is_active = False

        await self.db.flush()
        await self.db.refresh(category)

        return True
