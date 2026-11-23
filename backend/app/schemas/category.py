from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    type: Literal["income", "expense"]
    color: str | None = Field(default=None, max_length=20)
    icon: str | None = Field(default=None, max_length=50)


# Update category request
class CategoryUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    color: str | None = Field(default=None, max_length=20)
    icon: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")


# Category response
class CategoryResponse(BaseModel):

    id: str
    user_id: str
    name: str
    type: Literal["income", "expense"]
    color: str | None
    icon: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
