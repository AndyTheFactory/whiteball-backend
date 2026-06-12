"""Dictionary reference schemas."""

from uuid import UUID

from pydantic import BaseModel


class DictionaryValueResponse(BaseModel):
    """Dictionary value response schema."""

    id: UUID
    dictionary_type_code: str
    code: str
    name_ro: str
    name_en: str | None = None
    is_active: bool
    sort_order: int

    class Config:
        from_attributes = True
