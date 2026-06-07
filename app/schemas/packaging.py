"""Packaging schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class PackagingItemCreate(BaseModel):
    """Packaging item creation schema."""

    type: str = Field(..., min_length=1, max_length=50)
    subtype: str | None = Field(None, max_length=100)
    material: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    weight_grams: Decimal = Field(..., ge=0)


class PackagingItemUpdate(BaseModel):
    """Packaging item update schema."""

    type: str | None = Field(None, min_length=1, max_length=50)
    subtype: str | None = Field(None, max_length=100)
    material: str | None = Field(None, min_length=1, max_length=100)
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    weight_grams: Decimal | None = Field(None, ge=0)


class PackagingItemResponse(BaseSchema):
    """Packaging item response schema."""

    type: str
    subtype: str | None = None
    material: str
    name: str
    description: str | None = None
    weight_grams: Decimal
    company_id: UUID
    matched_with_reference_id: UUID | None = None


class ProductPackagingInput(BaseModel):
    """Product packaging input for association creation."""

    packaging_item_id: UUID | None = None
    packaging_item: PackagingItemCreate | None = None
    quantity_per_product_unit: Decimal = Field(default=Decimal(1), ge=0)
    applies_to_unit: str = Field(default="unit", max_length=50)
    notes: str | None = None


class PackagingAssociationResponse(BaseModel):
    """Product packaging association response."""

    association_id: UUID
    packaging_item_id: UUID
    type: str
    subtype: str | None = None
    material: str
    name: str
    weight_grams: Decimal
    quantity_per_product_unit: Decimal
    applies_to_unit: str = "unit"
    notes: str | None = None

    class Config:
        from_attributes = True


class PackagingAssociationUpdate(BaseModel):
    """Product packaging association update."""

    quantity_per_product_unit: Decimal | None = Field(None, ge=0)
    applies_to_unit: str | None = Field(None, max_length=50)
    notes: str | None = None
    packaging_item: PackagingItemUpdate | None = None
