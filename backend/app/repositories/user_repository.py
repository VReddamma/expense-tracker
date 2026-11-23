from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))

        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str):
        result = await self.db.execute(select(User).where(User.id == user_id))

        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate, hashed_password: str):
        new_user = User(
            name=user_data.name, email=user_data.email, hashed_password=hashed_password
        )

        self.db.add(new_user)

        await self.db.flush()
        await self.db.refresh(new_user)

        return new_user
