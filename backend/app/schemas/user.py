from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Registration request
class UserCreate(BaseModel):

    name: str = Field(min_length=2, max_length=100)

    email: EmailStr

    password: str = Field(min_length=8, max_length=128)


# Login request
class UserLogin(BaseModel):

    email: EmailStr

    password: str = Field(min_length=8, max_length=128)


# User response
class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Profile update request
class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)

    email: EmailStr | None = None

    model_config = ConfigDict(extra="forbid")


# Login token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
