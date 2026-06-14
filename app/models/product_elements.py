"""Product elements model."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product


class ProductElement(Base):
    """Product element model - represents components/materials that make up a product."""

    __tablename__ = "product_elements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    classification_code: Mapped[str] = mapped_column(String(50), ForeignKey("dictionary_values.code"), nullable=False)
    type_code: Mapped[str | None] = mapped_column(String(50), ForeignKey("dictionary_values.code"), nullable=True)
    material_code: Mapped[str | None] = mapped_column(String(50), ForeignKey("dictionary_values.code"), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight_grams: Mapped[Decimal | None] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    attributes: Mapped[dict[str, object]] = mapped_column(JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product")

    # Index on product_id (defined in migration)
    __table_args__ = (Index("ix_product_elements_product_id", "product_id"),)
