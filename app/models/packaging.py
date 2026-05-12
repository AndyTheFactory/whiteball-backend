"""Packaging item and reference models."""
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class PackagingItem(Base):
    """Packaging item model."""
    
    __tablename__ = "packaging_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # primary, secondary, tertiary
    subtype = Column(String(100), nullable=True)  # commercial, municipal, unknown
    material = Column(String(100), nullable=False)  # plastic, pet, glass, etc.
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    weight_grams = Column(Numeric(precision=10, scale=2), nullable=False)
    matched_with_reference_id = Column(
        UUID(as_uuid=True),
        ForeignKey("whiteball_packaging_items.id"),
        nullable=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company")
    product_associations = relationship("ProductPackagingAssociation", back_populates="packaging_item")
    reference_item = relationship("WhiteballPackagingItem")


class WhiteballPackagingItem(Base):
    """Whiteball packaging reference model."""
    
    __tablename__ = "whiteball_packaging_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)
    subtype = Column(String(100), nullable=True)
    material = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    weight_grams = Column(Numeric(precision=10, scale=2), nullable=True)
    source_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
