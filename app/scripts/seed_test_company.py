"""Seed script for creating test company and user."""

import uuid

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db import SessionLocal
from app.db.base import Base
from app.db.session import engine
from app.models.company import Company
from app.models.user import User

settings = get_settings()


def seed_db() -> None:
    """Create test company and user."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        # Check if test company already exists
        from sqlalchemy import select

        stmt = select(Company).where(Company.name == "Whiteball Test Company")
        existing_company = db.execute(stmt).scalars().first()

        if existing_company:
            print("Test company already exists, skipping seed...")
            return

        # Create test company
        company = Company(
            id=uuid.uuid4(),
            name="Whiteball Test Company",
            role="customer",
            is_active=True,
            country="US",
            city="Test City",
            phone_number="+1234567890",
        )
        db.add(company)
        db.flush()

        # Create test user
        user = User(
            id=uuid.uuid4(),
            company_id=company.id,
            email=settings.test_admin_email,
            password_hash=get_password_hash(settings.test_admin_password),
            full_name="Test Admin",
            role="admin",
            is_active=True,
        )
        db.add(user)

        db.commit()

        print(f"✓ Test company created: {company.name}")
        print(f"✓ Test user created: {user.email}")
        print(f"  Password: {settings.test_admin_password}")

    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
