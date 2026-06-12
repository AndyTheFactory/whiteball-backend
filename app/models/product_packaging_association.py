"""Product classification association model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product


class ProductClassification(Base):
    """Association between products and dictionary classifications."""

    __tablename__ = "product_classifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    classification_code: Mapped[str] = mapped_column(String(50), ForeignKey("dictionary_values.code"), nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="classifications")


ProductPackagingAssociation = ProductClassification
