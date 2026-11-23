from fastapi import APIRouter, Depends, Response, Cookie, status
from sqlalchemy.ext.asyncio import AsyncSession

# DB
from app.db.database import get_db

# CORE
from app.core.security import create_access_token
from app.core.dependencies import get_current_user
from app.core.exceptions import UnauthorizedException

# SCHEMAS
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
)

# SERVICES
from app.services.auth_service import AuthService
from app.services.refresh_token_service import RefreshTokenService

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Register
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    return await auth_service.register_user(user_data)


# Login
@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_data: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    # 1. Verify email and password
    user = await auth_service.authenticate_user(user_data.email, user_data.password)

    # 2. Generate access token
    access_token = create_access_token(user.id)

    # 3. Generate and store refresh token
    refresh_service = RefreshTokenService(db)

    refresh_token = await refresh_service.create_refresh_token(user.id)

    # 4. Store refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    # 5. Return access token and user
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


# Get currently logged-in user
@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user=Depends(get_current_user),
):
    return current_user


# Refresh access token
@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise UnauthorizedException("Refresh token missing")

    refresh_service = RefreshTokenService(db)

    # 1. Validate old token and rotate it
    result = await refresh_service.rotate_refresh_token(refresh_token)

    user = result["user"]
    new_refresh_token = result["refresh_token"]

    # 2. Generate new access token
    access_token = create_access_token(user.id)

    # 3. Set replacement refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    # 4. Return new access token and user
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


# Logout
@router.post("/logout")
async def logout_user(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise UnauthorizedException("Refresh token missing")

    refresh_service = RefreshTokenService(db)

    # 1. Revoke refresh token in database
    await refresh_service.revoke_refresh_token(refresh_token)

    # 2. Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {"message": "Logged out successfully"}
