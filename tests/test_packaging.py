"""Packaging-related tests."""

from fastapi.testclient import TestClient

from app.models.user import User


def _create_product(client: TestClient, auth_headers: dict) -> str:
    """Create a product used for scoped product elements endpoints."""
    response = client.post(
        "/api/v1/products",
        json={
            "sku": "PROD-001",
            "name": "Scoped Product",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_product_element(client: TestClient, auth_headers: dict, seed_dictionary_data: None):
    """Test creating a product element."""
    product_id = _create_product(client, auth_headers)

    response = client.post(
        f"/api/v1/products/{product_id}/elements",
        json={
            "classification_code": "packaging",
            "type_code": "primary",
            "material_code": "other_plastics",
            "name": "Plastic Bottle",
            "description": "500ml PET bottle",
            "weight_grams": 25.5,
            "attributes": {"color": "clear"},
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["classification_code"] == "packaging"
    assert data["type_code"] == "primary"
    assert data["material_code"] == "other_plastics"
    assert data["name"] == "Plastic Bottle"
    assert data["attributes"]["color"] == "clear"


def test_update_product_element(client: TestClient, auth_headers: dict, seed_dictionary_data: None):
    """Test updating a product element."""
    product_id = _create_product(client, auth_headers)

    create_response = client.post(
        f"/api/v1/products/{product_id}/elements",
        json={
            "classification_code": "packaging",
            "type_code": "primary",
            "material_code": "other_plastics",
            "name": "Original Name",
            "weight_grams": 25.5,
        },
        headers=auth_headers,
    )
    item_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/products/{product_id}/elements/{item_id}",
        params={"classification_code": "packaging"},
        json={
            "name": "Updated Name",
            "weight_grams": 30.0,
            "attributes": {"updated": True},
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert float(data["weight_grams"]) == 30.0
    assert data["attributes"]["updated"] is True


def test_list_product_elements(client: TestClient, auth_headers: dict, seed_dictionary_data: None):
    """Test listing product elements."""
    product_id = _create_product(client, auth_headers)

    for i in range(3):
        client.post(
            f"/api/v1/products/{product_id}/elements",
            json={
                "classification_code": "packaging",
                "type_code": "primary",
                "material_code": "other_plastics",
                "name": f"Element {i}",
                "weight_grams": 25 + i,
            },
            headers=auth_headers,
        )

    response = client.get(f"/api/v1/products/{product_id}/elements", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_list_whiteball_reference_items(client: TestClient, auth_headers: dict, reference_packaging_item):
    """Test listing Whiteball reference packaging items."""
    response = client.get("/api/v1/whiteball-packaging-items", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["source_id"] == reference_packaging_item.source_id


def test_create_update_delete_product_classification(
    client: TestClient, auth_headers: dict, seed_dictionary_data: None, test_user: User
):
    """Test creating, updating, and deleting a product classification."""
    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "PROD-001",
            "name": "Test Product",
            "classification_count": 0,
        },
        headers=auth_headers,
    )
    product_id = product_response.json()["id"]

    create_response = client.post(
        f"/api/v1/products/{product_id}/classifications",
        json={"classification_code": "packaging"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    association_id = create_response.json()["association_id"]
    assert create_response.json()["classification_code"] == "packaging"

    list_response = client.get(f"/api/v1/products/{product_id}/classifications", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/api/v1/products/{product_id}/classifications/{association_id}",
        json={"classification_code": "scp"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["classification_code"] == "scp"

    delete_response = client.delete(
        f"/api/v1/products/{product_id}/classifications/{association_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    final_list_response = client.get(f"/api/v1/products/{product_id}/classifications", headers=auth_headers)
    assert final_list_response.status_code == 200
    assert final_list_response.json() == []


def test_delete_product_element(client: TestClient, auth_headers: dict, seed_dictionary_data: None):
    """Test removing a product element."""
    product_id = _create_product(client, auth_headers)

    create_response = client.post(
        f"/api/v1/products/{product_id}/elements",
        json={
            "classification_code": "packaging",
            "type_code": "primary",
            "material_code": "other_plastics",
            "name": "Delete Me",
            "weight_grams": 25.5,
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    response = client.delete(
        f"/api/v1/products/{product_id}/elements",
        params={"classification_code": "packaging"},
        headers=auth_headers,
    )
    assert response.status_code == 204

    list_response = client.get(f"/api/v1/products/{product_id}/elements", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0
