"""Authentication tests."""

from fastapi.testclient import TestClient

from app.models.user import User


def test_login_success(client: TestClient, test_user: User):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "test123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email
    assert data["user"]["role"] == "admin"


def test_login_invalid_password(client: TestClient, test_user: User):
    """Test login with invalid password."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "AUTH_INVALID_CREDENTIALS"


def test_login_nonexistent_user(client: TestClient, test_user: User):
    """Test login with nonexistent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "test123",
        },
    )

    assert response.status_code == 401


def test_get_current_user(client: TestClient, auth_headers: dict):
    """Test getting current user info."""
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "admin"
    assert data["is_active"] is True


def test_protected_endpoint_requires_token(client: TestClient):
    """Test that protected endpoints require authentication."""
    response = client.get("/api/v1/products")

    assert response.status_code == 401
