"""Company schemas."""

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class CompanyCreate(BaseModel):
    """Company creation schema."""

    name: str = Field(..., min_length=1, max_length=255)
    address_type: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    county: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    street: str | None = Field(None, max_length=255)
    street_number: str | None = Field(None, max_length=50)
    building: str | None = Field(None, max_length=50)
    entrance: str | None = Field(None, max_length=50)
    floor: str | None = Field(None, max_length=50)
    apartment: str | None = Field(None, max_length=50)
    additional_address_info: str | None = None
    vat_number: str | None = Field(None, max_length=50)
    registration_number: str | None = Field(None, max_length=50)
    phone_number: str | None = Field(None, max_length=20)
    role: str = Field("customer", pattern="^(admin|customer)$")


class CompanyUpdate(BaseModel):
    """Company update schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    address_type: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    county: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    street: str | None = Field(None, max_length=255)
    street_number: str | None = Field(None, max_length=50)
    building: str | None = Field(None, max_length=50)
    entrance: str | None = Field(None, max_length=50)
    floor: str | None = Field(None, max_length=50)
    apartment: str | None = Field(None, max_length=50)
    additional_address_info: str | None = None
    vat_number: str | None = Field(None, max_length=50)
    registration_number: str | None = Field(None, max_length=50)
    phone_number: str | None = Field(None, max_length=20)
    role: str | None = Field(None, pattern="^(admin|customer)$")
    is_active: bool | None = None


class CompanyResponse(BaseSchema):
    """Company response schema."""

    name: str
    address_type: str | None = None
    country: str | None = None
    county: str | None = None
    city: str | None = None
    postal_code: str | None = None
    street: str | None = None
    street_number: str | None = None
    building: str | None = None
    entrance: str | None = None
    floor: str | None = None
    apartment: str | None = None
    additional_address_info: str | None = None
    vat_number: str | None = None
    registration_number: str | None = None
    phone_number: str | None = None
    role: str
    is_active: bool
