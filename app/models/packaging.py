"""Product element and reference models."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.company import Company


class PackagingItem(Base):
    """Company-owned product element model."""

    __tablename__ = "product_elements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    classification_code: Mapped[str] = mapped_column(String(50), ForeignKey("dictionary_values.code"), nullable=False)
    type_code: Mapped[str | None] = mapped_column(String(50), ForeignKey("dictionary_values.code"), nullable=True)
    material_code: Mapped[str] = mapped_column(String(50), ForeignKey("dictionary_values.code"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight_grams: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    attributes: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company")


class WhiteballPackagingItem(Base):
    """Whiteball packaging reference model."""

    __tablename__ = "whiteball_packaging_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    subtype: Mapped[str | None] = mapped_column(String(100), nullable=True)
    material: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight_grams: Mapped[Decimal | None] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
