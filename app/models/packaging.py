"""Packaging item and reference models."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.product_packaging_association import ProductPackagingAssociation


class PackagingItem(Base):
    """Packaging item model."""

    __tablename__ = "packaging_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # primary, secondary, tertiary
    subtype: Mapped[str | None] = mapped_column(String(100), nullable=True)  # commercial, municipal, unknown
    material: Mapped[str] = mapped_column(String(100), nullable=False)  # plastic, pet, glass, etc.
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight_grams: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    matched_with_reference_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("whiteball_packaging_items.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company")
    product_associations: Mapped[list["ProductPackagingAssociation"]] = relationship(
        "ProductPackagingAssociation", back_populates="packaging_item"
    )
    reference_item: Mapped["WhiteballPackagingItem | None"] = relationship("WhiteballPackagingItem")


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
