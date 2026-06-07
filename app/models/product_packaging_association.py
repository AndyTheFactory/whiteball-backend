"""Product packaging association model."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.packaging import PackagingItem
    from app.models.product import Product


class ProductPackagingAssociation(Base):
    """Association between products and packaging items."""

    __tablename__ = "product_packaging_associations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    packaging_item_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("packaging_items.id"), nullable=False, index=True
    )
    quantity_per_product_unit: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), default=1, nullable=False
    )
    applies_to_unit: Mapped[str] = mapped_column(String(50), default="unit", nullable=False)  # unit, case, pallet
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="packaging_associations")
    packaging_item: Mapped["PackagingItem"] = relationship("PackagingItem", back_populates="product_associations")
