"""Packaging tests."""

from fastapi.testclient import TestClient


def test_create_packaging_item(client: TestClient, auth_headers: dict):
    """Test creating a packaging item."""
    response = client.post(
        "/api/v1/packaging-items",
        json={
            "type": "primary",
            "subtype": "commercial",
            "material": "plastic",
            "name": "Plastic Bottle",
            "description": "500ml PET bottle",
            "weight_grams": 25.5,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "primary"
    assert data["material"] == "plastic"
    assert data["name"] == "Plastic Bottle"


def test_update_packaging_item(client: TestClient, auth_headers: dict):
    """Test updating a packaging item."""
    # Create packaging item
    create_response = client.post(
        "/api/v1/packaging-items",
        json={
            "type": "primary",
            "material": "plastic",
            "name": "Original Name",
            "weight_grams": 25.5,
        },
        headers=auth_headers,
    )
    item_id = create_response.json()["id"]

    # Update item
    response = client.patch(
        f"/api/v1/packaging-items/{item_id}",
        json={
            "name": "Updated Name",
            "weight_grams": 30.0,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert float(data["weight_grams"]) == 30.0


def test_list_packaging_items(client: TestClient, auth_headers: dict):
    """Test listing packaging items."""
    # Create items
    for i in range(3):
        client.post(
            "/api/v1/packaging-items",
            json={
                "type": "primary",
                "material": "plastic",
                "name": f"Item {i}",
                "weight_grams": 25 + i,
            },
            headers=auth_headers,
        )

    response = client.get(
        "/api/v1/packaging-items",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3


def test_associate_packaging_with_product(client: TestClient, auth_headers: dict):
    """Test associating packaging with a product."""
    # Create product
    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "PROD-001",
            "name": "Test Product",
        },
        headers=auth_headers,
    )
    product_id = product_response.json()["id"]

    # Associate packaging
    response = client.post(
        f"/api/v1/products/{product_id}/packaging",
        json={
            "packaging_item": {
                "type": "primary",
                "material": "plastic",
                "name": "Plastic Bottle",
                "weight_grams": 25.5,
            },
            "quantity_per_product_unit": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "primary"
    assert data["quantity_per_product_unit"] == 1


def test_update_product_packaging_association(client: TestClient, auth_headers: dict):
    """Test updating a product packaging association."""
    # Create product
    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "PROD-002",
            "name": "Test Product",
        },
        headers=auth_headers,
    )
    product_id = product_response.json()["id"]

    # Associate packaging
    assoc_response = client.post(
        f"/api/v1/products/{product_id}/packaging",
        json={
            "packaging_item": {
                "type": "primary",
                "material": "plastic",
                "name": "Plastic Bottle",
                "weight_grams": 25.5,
            },
            "quantity_per_product_unit": 1,
        },
        headers=auth_headers,
    )
    association_id = assoc_response.json()["association_id"]

    # Update association
    response = client.patch(
        f"/api/v1/products/{product_id}/packaging/{association_id}",
        json={
            "quantity_per_product_unit": 2,
            "notes": "Updated note",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["quantity_per_product_unit"] == 2
    assert data["notes"] == "Updated note"


def test_remove_packaging_from_product(client: TestClient, auth_headers: dict):
    """Test removing packaging from product."""
    # Create product
    product_response = client.post(
        "/api/v1/products",
        json={
            "sku": "PROD-003",
            "name": "Test Product",
        },
        headers=auth_headers,
    )
    product_id = product_response.json()["id"]

    # Associate packaging
    assoc_response = client.post(
        f"/api/v1/products/{product_id}/packaging",
        json={
            "packaging_item": {
                "type": "primary",
                "material": "plastic",
                "name": "Plastic Bottle",
                "weight_grams": 25.5,
            },
        },
        headers=auth_headers,
    )
    association_id = assoc_response.json()["association_id"]

    # Remove association
    response = client.delete(
        f"/api/v1/products/{product_id}/packaging/{association_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # Verify product detail doesn't include the packaging
    detail_response = client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    assert len(detail_response.json()["packaging"]) == 0
