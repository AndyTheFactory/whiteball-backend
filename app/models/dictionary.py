"""Dictionary reference models."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product_classification import ProductClassification
    from app.models.product_elements import ProductElements


class DictionaryType(Base):
    """Dictionary type grouping model."""

    __tablename__ = "dictionary_types"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    values: Mapped[list["DictionaryValue"]] = relationship("DictionaryValue", back_populates="dictionary_type")


class DictionaryValue(Base):
    """Dictionary value model."""

    __tablename__ = "dictionary_values"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dictionary_type_code: Mapped[str] = mapped_column(
        String(100), ForeignKey("dictionary_types.code", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_ro: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    dictionary_type: Mapped["DictionaryType"] = relationship("DictionaryType", back_populates="values")
    product_classifications: Mapped[list["ProductClassification"]] = relationship(
        "ProductClassification", backref="dictionary_value"
    )
    product_elements_as_classification: Mapped[list["ProductElements"]] = relationship(
        "ProductElements", foreign_keys="ProductElements.classification_code", backref="classification_value"
    )
    product_elements_as_type: Mapped[list["ProductElements"]] = relationship(
        "ProductElements", foreign_keys="ProductElements.type_code", backref="type_value"
    )
    product_elements_as_material: Mapped[list["ProductElements"]] = relationship(
        "ProductElements", foreign_keys="ProductElements.material_code", backref="material_value"
    )
