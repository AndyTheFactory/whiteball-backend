"""User schemas."""

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class UserCreate(BaseModel):
    """User creation schema."""

    company_id: str = Field(..., description="Company UUID")
    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    full_name: str | None = Field(None, max_length=255)
    phone_number: str | None = Field(None, max_length=20)
    role: str = Field("user", pattern="^(admin|user)$")


class UserUpdate(BaseModel):
    """User update schema."""

    email: str | None = Field(None, min_length=1, max_length=255)
    full_name: str | None = Field(None, max_length=255)
    phone_number: str | None = Field(None, max_length=20)
    role: str | None = Field(None, pattern="^(admin|user)$")
    is_active: bool | None = None


class UserResponse(BaseSchema):
    """User response schema."""

    email: str
    company_id: str
    full_name: str | None = None
    phone_number: str | None = None
    role: str
    is_active: bool
