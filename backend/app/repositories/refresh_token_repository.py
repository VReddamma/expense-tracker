from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Create refresh token record
    async def create(self, user_id: str, token_hash: str, expires_at):
        refresh_token = RefreshToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )

        self.db.add(refresh_token)

        await self.db.flush()
        await self.db.refresh(refresh_token)

        return refresh_token

    # Get refresh token by hash
    async def get_by_hash(self, token_hash: str):
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )

        return result.scalar_one_or_none()

    # Revoke refresh token
    async def revoke(self, refresh_token: RefreshToken):
        from datetime import datetime, timezone

        refresh_token.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await self.db.flush()

        return refresh_token
