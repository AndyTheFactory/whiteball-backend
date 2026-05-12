"""Pytest configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
import uuid
from app.main import create_app
from app.db.base import Base
from app.models.company import Company
from app.models.user import User
from app.core.security import get_password_hash
from app.api.deps import get_db

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
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
def auth_headers(client: TestClient, test_user: User):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "test123",
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
