from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository


class UserService:

    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.db = db

    # Get user by email
    async def get_user_by_email(self, email: str):
        return await self.user_repo.get_by_email(email)

    # Get user by ID
    async def get_user_by_id(self, user_id: str):
        return await self.user_repo.get_by_id(user_id)
