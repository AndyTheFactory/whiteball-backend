"""Pytest configuration and fixtures."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import get_password_hash
from app.db.base import Base
from app.main import create_app
from app.models.company import Company
from app.models.dictionary import DictionaryType, DictionaryValue
from app.models.packaging import WhiteballPackagingItem
from app.models.user import User

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db: Session):
    """Create test client."""
    app = create_app()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


@pytest.fixture()
def test_company(db: Session) -> Company:
    """Create test company."""
    company = Company(
        id=uuid.uuid4(),
        name="Test Company",
        role="customer",
        is_active=True,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture()
def test_user(db: Session, test_company: Company) -> User:
    """Create test user."""
    user = User(
        id=uuid.uuid4(),
        company_id=test_company.id,
        email="test@example.com",
        password_hash=get_password_hash("test123"),
        full_name="Test User",
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def seed_dictionary_data(db: Session) -> None:
    """Seed the minimal dictionary reference data used by packaging tests."""
    classification_type = DictionaryType(id=uuid.uuid4(), code="classification_code", name="Classification Code")
    type_type = DictionaryType(id=uuid.uuid4(), code="type_code", name="Type Code")
    material_type = DictionaryType(id=uuid.uuid4(), code="material_code", name="Material Code")
    db.add_all([classification_type, type_type, material_type])
    db.add_all(
        [
            DictionaryValue(
                id=uuid.uuid4(),
                dictionary_type_code="classification_code",
                code="ambalaje",
                name_ro="Ambalaje",
                name_en="Packaging",
                is_active=True,
                sort_order=0,
            ),
            DictionaryValue(
                id=uuid.uuid4(),
                dictionary_type_code="classification_code",
                code="scp",
                name_ro="SCP",
                name_en="SCP",
                is_active=True,
                sort_order=0,
            ),
            DictionaryValue(
                id=uuid.uuid4(),
                dictionary_type_code="type_code",
                code="primary",
                name_ro="Primar",
                name_en="Primary",
                is_active=True,
                sort_order=0,
            ),
            DictionaryValue(
                id=uuid.uuid4(),
                dictionary_type_code="material_code",
                code="other_plastics",
                name_ro="Alte plastice",
                name_en="Other Plastics",
                is_active=True,
                sort_order=0,
            ),
        ]
    )
    db.commit()


@pytest.fixture()
def reference_packaging_item(db: Session, seed_dictionary_data: None) -> WhiteballPackagingItem:
    """Create a Whiteball reference packaging item for tests."""
    item = WhiteballPackagingItem(
        id=uuid.uuid4(),
        type="primary",
        subtype=None,
        material="other_plastics",
        name="Reference Bottle",
        description="Reference packaging item",
        weight_grams=25.5,
        source_id="REF-001",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture()
def auth_headers(client: TestClient, test_user: User):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "test123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
