"""Authentication schemas."""

from uuid import UUID

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Login request schema."""

    email: str
    password: str


class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    email: str
    company_id: UUID
    role: str
    full_name: str | None = None
    is_active: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data."""

    sub: str  # user_id
    company_id: str
    role: str
    exp: int
