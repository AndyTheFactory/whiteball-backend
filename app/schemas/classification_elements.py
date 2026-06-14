"""Classification-specific product element schemas.

Each classification has its own input/output schema. Non-standard fields
(those not directly mapped to ProductElements columns) are stored in the
``attributes`` JSONB column.
"""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Shared base for all classification responses
# ---------------------------------------------------------------------------


class ClassificationElementBase(BaseModel):
    id: UUID

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# packaging
# ---------------------------------------------------------------------------


class PackagingElementInput(BaseModel):
    type_code: str | None = Field(None, max_length=50)
    material_code: str | None = Field(None, max_length=50)
    name: str | None = Field(None, max_length=255)
    weight_grams: Decimal | None = Field(None, ge=0)
    grouping: str | None = None


class PackagingElementResponse(ClassificationElementBase):
    type_code: str | None = None
    material_code: str | None = None
    name: str | None = None
    weight_grams: Decimal | None = None
    grouping: str | None = None


# ---------------------------------------------------------------------------
# scp
# ---------------------------------------------------------------------------


class ScpElementInput(BaseModel):
    product_value: Decimal | None = None


class ScpElementResponse(ClassificationElementBase):
    product_value: Decimal | None = None


# ---------------------------------------------------------------------------
# tire
# ---------------------------------------------------------------------------


class TireElementInput(BaseModel):
    weight_grams: Decimal | None = Field(None, ge=0)


class TireElementResponse(ClassificationElementBase):
    weight_grams: Decimal | None = None


# ---------------------------------------------------------------------------
# transport_pack
# ---------------------------------------------------------------------------


class TransportPackElementInput(BaseModel):
    name: str | None = Field(None, max_length=255)
    material_code: str | None = Field(None, max_length=50)
    thickness_micron: Decimal | None = None
    weight_grams: Decimal | None = Field(None, ge=0)


class TransportPackElementResponse(ClassificationElementBase):
    name: str | None = None
    material_code: str | None = None
    thickness_micron: Decimal | None = None
    weight_grams: Decimal | None = None


# ---------------------------------------------------------------------------
# oil
# ---------------------------------------------------------------------------


class OilElementInput(BaseModel):
    quantity: Decimal | None = None
    measure_unit: str | None = None


class OilElementResponse(ClassificationElementBase):
    quantity: Decimal | None = None
    measure_unit: str | None = None


# ---------------------------------------------------------------------------
# eee
# ---------------------------------------------------------------------------


class EeeElementInput(BaseModel):
    height_mm: Decimal | None = None
    width_mm: Decimal | None = None
    depth_mm: Decimal | None = None
    weight_grams: Decimal | None = Field(None, ge=0)
    category_code: str | None = Field(None, max_length=50)


class EeeElementResponse(ClassificationElementBase):
    height_mm: Decimal | None = None
    width_mm: Decimal | None = None
    depth_mm: Decimal | None = None
    weight_grams: Decimal | None = None
    category_code: str | None = None


# ---------------------------------------------------------------------------
# batteries
# ---------------------------------------------------------------------------


class BatteryElementInput(BaseModel):
    chemical_composition_code: str | None = Field(None, max_length=50)
    weight_grams: Decimal | None = Field(None, ge=0)
    category_code: str | None = Field(None, max_length=50)


class BatteryElementResponse(ClassificationElementBase):
    chemical_composition_code: str | None = None
    weight_grams: Decimal | None = None
    category_code: str | None = None


# ---------------------------------------------------------------------------
# sgr
# ---------------------------------------------------------------------------


class SgrElementInput(BaseModel):
    material_code: str | None = Field(None, max_length=50)
    color_code: str | None = None
    has_uv_protection: bool | None = None
    volume_ml: Decimal | None = None
    height_wo_cap_mm: Decimal | None = None
    height_w_cap_mm: Decimal | None = None
    diameter_mm: Decimal | None = None
    weight_grams: Decimal | None = Field(None, ge=0)


class SgrElementResponse(ClassificationElementBase):
    material_code: str | None = None
    color_code: str | None = None
    has_uv_protection: bool | None = None
    volume_ml: Decimal | None = None
    height_wo_cap_mm: Decimal | None = None
    height_w_cap_mm: Decimal | None = None
    diameter_mm: Decimal | None = None
    weight_grams: Decimal | None = None


# ---------------------------------------------------------------------------
# sup
# ---------------------------------------------------------------------------


class SupElementInput(BaseModel):
    composition_code: str | None = Field(None, max_length=50)
    percentage_plastic: Decimal | None = None
    percentage_RPET: Decimal | None = None
    weight_grams: Decimal | None = Field(None, ge=0)


class SupElementResponse(ClassificationElementBase):
    composition_code: str | None = None
    percentage_plastic: Decimal | None = None
    percentage_RPET: Decimal | None = None
    weight_grams: Decimal | None = None
