"""Product schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class ProductCreate(BaseModel):
    """Product creation schema."""

    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    category: str | None = Field(None, max_length=255)
    case_pack_quantity: int | None = Field(None, ge=1)
    pallet_quantity: int | None = Field(None, ge=1)
    net_weight: Decimal | None = Field(None, ge=0)
    manufacturer: str | None = Field(None, max_length=255)
    description: str | None = None


class ProductUpdate(BaseModel):
    """Product update schema."""

    sku: str | None = Field(None, min_length=1, max_length=100)
    name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, max_length=255)
    case_pack_quantity: int | None = Field(None, ge=1)
    pallet_quantity: int | None = Field(None, ge=1)
    net_weight: Decimal | None = Field(None, ge=0)
    manufacturer: str | None = Field(None, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class ProductResponse(BaseSchema):
    """Product response schema."""

    sku: str
    name: str
    category: str | None = None
    case_pack_quantity: int | None = None
    pallet_quantity: int | None = None
    net_weight: Decimal | None = None
    manufacturer: str | None = None
    description: str | None = None
    is_active: bool
    company_id: UUID
    packaging_count: int = 0
    classification_count: int = 0


class ProductDetailResponse(ProductResponse):
    """Product detail response with packaging."""

    packaging: list[str] = []
    classifications: list[str] = []


ProductDetailResponse.model_rebuild()
