from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password
from app.core.exceptions import (
    ConflictException,
    UnauthorizedException,
    ForbiddenException,
)


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    # User registration
    async def register_user(self, user_data: UserCreate):

        # 1. Check whether email already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)

        if existing_user:
            raise ConflictException("Email already registered")

        # 2. Hash the password
        hashed_password = hash_password(user_data.password)

        try:
            # 3. Create user in database
            new_user = await self.user_repo.create(user_data, hashed_password)

            # 4. Commit transaction
            await self.db.commit()

            # 5. Return created user
            return new_user

        except Exception:
            await self.db.rollback()
            raise

    # Login
    async def authenticate_user(self, email: str, password: str):

        # 1. Find user by email
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise UnauthorizedException("Invalid email or password")

        # 2. Check whether user is active
        if not user.is_active:
            raise ForbiddenException("User account is inactive")

        # 3. Verify password
        is_valid = verify_password(password, user.hashed_password)

        if not is_valid:
            raise UnauthorizedException("Invalid email or password")

        # 4. Return authenticated user
        return user
