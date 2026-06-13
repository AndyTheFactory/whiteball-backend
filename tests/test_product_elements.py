"""Product element routes scoped by product tests."""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.company import Company
from app.models.user import User


def _create_product(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/products",
        json={
            "sku": f"SKU-{uuid.uuid4()}",
            "name": "Test Product",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_list_product_elements_with_optional_classification_filter(
    client: TestClient, auth_headers: dict[str, str], seed_dictionary_data: None
):
    """List endpoint returns only elements for the selected product and optional classification."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements",
        json={
            "classification_code": "ambalaje",
            "type_code": "primary",
            "material_code": "other_plastics",
            "name": "Bottle",
            "weight_grams": 12.5,
        },
        headers=auth_headers,
    )

    client.post(
        f"/api/v1/products/{product_id}/elements",
        json={
            "classification_code": "scp",
            "type_code": "primary",
            "material_code": "other_plastics",
            "name": "Label",
            "weight_grams": 1.0,
        },
        headers=auth_headers,
    )

    list_response = client.get(f"/api/v1/products/{product_id}/elements", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 2

    filtered = client.get(
        f"/api/v1/products/{product_id}/elements",
        params={"classification_code": "ambalaje"},
        headers=auth_headers,
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["classification_code"] == "ambalaje"


def test_patch_requires_classification_code(
    client: TestClient, auth_headers: dict[str, str], seed_dictionary_data: None
):
    """Patch endpoint enforces required classification_code query param."""
    product_id = _create_product(client, auth_headers)

    create_response = client.post(
        f"/api/v1/products/{product_id}/elements",
        json={
            "classification_code": "ambalaje",
            "type_code": "primary",
            "material_code": "other_plastics",
            "name": "Bottle",
            "weight_grams": 12.5,
        },
        headers=auth_headers,
    )
    item_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/products/{product_id}/elements/{item_id}",
        json={"name": "Updated Bottle"},
        headers=auth_headers,
    )

    assert response.status_code == 422

    valid_patch = client.patch(
        f"/api/v1/products/{product_id}/elements/{item_id}",
        params={"classification_code": "ambalaje"},
        json={"name": "Updated Bottle"},
        headers=auth_headers,
    )

    assert valid_patch.status_code == 200
    assert valid_patch.json()["name"] == "Updated Bottle"


def test_delete_all_by_product_and_classification(
    client: TestClient, auth_headers: dict[str, str], seed_dictionary_data: None
):
    """Delete endpoint removes all elements matching product_id and classification_code."""
    product_id = _create_product(client, auth_headers)

    for classification_code in ("ambalaje", "ambalaje", "scp"):
        client.post(
            f"/api/v1/products/{product_id}/elements",
            json={
                "classification_code": classification_code,
                "type_code": "primary",
                "material_code": "other_plastics",
                "name": f"Element-{classification_code}",
                "weight_grams": 10,
            },
            headers=auth_headers,
        )

    delete_response = client.delete(
        f"/api/v1/products/{product_id}/elements",
        params={"classification_code": "ambalaje"},
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    list_response = client.get(f"/api/v1/products/{product_id}/elements", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert list_response.json()["items"][0]["classification_code"] == "scp"


def test_product_elements_are_company_scoped(
    client: TestClient,
    db: Session,
    auth_headers: dict[str, str],
    seed_dictionary_data: None,
):
    """A user from another company cannot manipulate product elements for the product."""
    product_id = _create_product(client, auth_headers)

    other_company = Company(id=uuid.uuid4(), name="Other Co", role="customer", is_active=True)
    other_user = User(
        id=uuid.uuid4(),
        company_id=other_company.id,
        email="other@example.com",
        password_hash=get_password_hash("other123"),
        full_name="Other User",
        role="admin",
        is_active=True,
    )
    db.add_all([other_company, other_user])
    db.commit()

    login = client.post("/api/v1/auth/login", json={"email": "other@example.com", "password": "other123"})
    assert login.status_code == 200
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    create_response = client.post(
        f"/api/v1/products/{product_id}/elements",
        json={
            "classification_code": "ambalaje",
            "type_code": "primary",
            "material_code": "other_plastics",
            "name": "Unauthorized",
            "weight_grams": 1,
        },
        headers=other_headers,
    )

    assert create_response.status_code == 404
