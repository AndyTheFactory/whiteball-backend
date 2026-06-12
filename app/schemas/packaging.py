"""Packaging and classification schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class ProductElementCreate(BaseModel):
    """Product element creation schema."""

    classification_code: str = Field(..., min_length=1, max_length=50)
    type_code: str | None = Field(None, max_length=50)
    material_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    weight_grams: Decimal = Field(..., ge=0)
    attributes: dict[str, object] = Field(default_factory=dict)


class ProductElementUpdate(BaseModel):
    """Product element update schema."""

    classification_code: str | None = Field(None, min_length=1, max_length=50)
    type_code: str | None = Field(None, max_length=50)
    material_code: str | None = Field(None, min_length=1, max_length=50)
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    weight_grams: Decimal | None = Field(None, ge=0)
    attributes: dict[str, object] | None = None


class ProductElementResponse(BaseSchema):
    """Product element response schema."""

    company_id: UUID
    classification_code: str
    type_code: str | None = None
    material_code: str
    name: str
    description: str | None = None
    weight_grams: Decimal
    attributes: dict[str, object] = Field(default_factory=dict)


class WhiteballPackagingItemResponse(BaseSchema):
    """Whiteball packaging reference response schema."""

    type: str
    subtype: str | None = None
    material: str
    name: str
    description: str | None = None
    weight_grams: Decimal | None = None
    source_id: str | None = None


class ProductClassificationCreate(BaseModel):
    """Create a product classification."""

    classification_code: str = Field(..., min_length=1, max_length=50)


class ProductClassificationResponse(BaseModel):
    """Product classification response."""

    association_id: UUID
    product_id: UUID
    classification_code: str
    name_ro: str | None = None
    name_en: str | None = None
    is_active: bool | None = None

    class Config:
        from_attributes = True


class ProductClassificationUpdate(BaseModel):
    """Product classification update schema."""

    classification_code: str | None = Field(None, min_length=1, max_length=50)
