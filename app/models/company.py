"""Company model."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Company(Base):
    """Company model."""

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    county: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    street: Mapped[str | None] = mapped_column(String(255), nullable=True)
    street_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    building: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entrance: Mapped[str | None] = mapped_column(String(50), nullable=True)
    floor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    apartment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    additional_address_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    vat_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="customer", nullable=False)  # admin, customer
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
