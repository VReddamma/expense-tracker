from datetime import datetime, timedelta, timezone

import jwt
import hashlib
import secrets
import hmac

from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import UnauthorizedException

# Password hashing
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# Generate JWT access token
def create_access_token(user_id: str) -> str:

    now = datetime.now(timezone.utc)

    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "iat": now,
        "exp": expire,
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return token


# Decode and verify JWT access token
def decode_access_token(token: str) -> dict:

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["sub", "iat", "exp"]},
        )

        user_id = payload.get("sub")

        if not isinstance(user_id, str) or not user_id.strip():
            raise UnauthorizedException("Invalid access token")

        return payload

    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid or expired access token")


# REFRESH TOKEN


# Generate a secure random refresh token
def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


# Hash refresh token using SHA-256
def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# Calculate refresh token expiration
def get_refresh_token_expiry() -> datetime:

    now = datetime.now(timezone.utc)

    expiry = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # MySQL DateTime column uses a timezone-naive datetime
    return expiry.replace(tzinfo=None)


# Compare refresh token hashes safely
def verify_refresh_token(token: str, stored_hash: str) -> bool:

    token_hash = hash_refresh_token(token)

    return hmac.compare_digest(token_hash, stored_hash)
