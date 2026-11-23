from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository

from app.core.security import (
    generate_refresh_token,
    hash_refresh_token,
    get_refresh_token_expiry,
    verify_refresh_token,
)

from app.core.exceptions import UnauthorizedException


class RefreshTokenService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.token_repo = RefreshTokenRepository(db)
        self.user_repo = UserRepository(db)

    # Create and store refresh token
    async def create_refresh_token(self, user_id: str):

        token = generate_refresh_token()
        token_hash = hash_refresh_token(token)
        expires_at = get_refresh_token_expiry()

        try:
            await self.token_repo.create(
                user_id=user_id, token_hash=token_hash, expires_at=expires_at
            )

            await self.db.commit()

            return token

        except Exception:
            await self.db.rollback()
            raise

    # Validate refresh token
    async def validate_refresh_token(self, token: str):

        token_hash = hash_refresh_token(token)

        stored_token = await self.token_repo.get_by_hash(token_hash)

        if not stored_token:
            raise UnauthorizedException("Invalid refresh token")

        if stored_token.revoked_at is not None:
            raise UnauthorizedException("Refresh token has been revoked")

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if stored_token.expires_at <= now:
            raise UnauthorizedException("Refresh token has expired")

        if not verify_refresh_token(token, stored_token.token_hash):
            raise UnauthorizedException("Invalid refresh token")

        return stored_token

    # Revoke refresh token
    async def revoke_refresh_token(self, token: str):

        token_hash = hash_refresh_token(token)

        stored_token = await self.token_repo.get_by_hash(token_hash)

        if not stored_token:
            raise UnauthorizedException("Invalid refresh token")

        if stored_token.revoked_at is not None:
            raise UnauthorizedException("Refresh token already revoked")

        try:
            await self.token_repo.revoke(stored_token)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return True

    # Rotate refresh token
    async def rotate_refresh_token(self, token: str):

        try:
            # 1. Validate existing refresh token
            stored_token = await self.validate_refresh_token(token)

            # 2. Check whether user exists and is active
            user = await self.user_repo.get_by_id(stored_token.user_id)

            if not user or not user.is_active:
                raise UnauthorizedException("User not found or inactive")

            # 3. Generate new refresh token
            new_token = generate_refresh_token()

            new_token_hash = hash_refresh_token(new_token)

            expires_at = get_refresh_token_expiry()

            # 4. Revoke old refresh token
            await self.token_repo.revoke(stored_token)

            # 5. Store new refresh token
            await self.token_repo.create(
                user_id=stored_token.user_id,
                token_hash=new_token_hash,
                expires_at=expires_at,
            )

            # 6. Commit both operations together
            await self.db.commit()

            return {
                "user_id": stored_token.user_id,
                "refresh_token": new_token,
                "user": user,
            }

        except Exception:
            await self.db.rollback()
            raise
