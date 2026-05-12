"""Product packaging association model."""
from sqlalchemy import Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class ProductPackagingAssociation(Base):
    """Association between products and packaging items."""
    
    __tablename__ = "product_packaging_associations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    packaging_item_id = Column(UUID(as_uuid=True), ForeignKey("packaging_items.id"), nullable=False, index=True)
    quantity_per_product_unit = Column(Numeric(precision=10, scale=2), default=1, nullable=False)
    applies_to_unit = Column(String(50), default="unit", nullable=False)  # unit, case, pallet
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="packaging_associations")
    packaging_item = relationship("PackagingItem", back_populates="product_associations")
