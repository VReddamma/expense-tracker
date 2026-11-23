from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.repositories.user_repository import UserRepository

# Extract Bearer token from Authorization header
bearer_scheme = HTTPBearer()


# Get currently authenticated user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    # 1. Extract token from Authorization header
    token = credentials.credentials

    # 2. Decode and validate JWT access token
    payload = decode_access_token(token)

    # 3. Get user ID from JWT payload
    user_id = payload.get("sub")

    if not user_id:
        raise UnauthorizedException("Invalid access token")

    # 4. Find user in database
    user_repo = UserRepository(db)

    user = await user_repo.get_by_id(user_id)

    # 5. Check whether user exists and is active
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    # 6. Return authenticated user
    return user
