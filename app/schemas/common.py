"""Common schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Base schema with common fields."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Paginated response model."""

    items: list
    total: int
    limit: int
    offset: int
