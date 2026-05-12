"""Company model."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Company(Base):
    """Company model."""

    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address_type = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    county = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    street = Column(String(255), nullable=True)
    street_number = Column(String(50), nullable=True)
    building = Column(String(50), nullable=True)
    entrance = Column(String(50), nullable=True)
    floor = Column(String(50), nullable=True)
    apartment = Column(String(50), nullable=True)
    additional_address_info = Column(Text, nullable=True)
    vat_number = Column(String(50), nullable=True)
    registration_number = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=True)
    role = Column(String(50), default="customer", nullable=False)  # admin, customer
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
