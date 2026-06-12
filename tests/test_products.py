"""Product tests."""

from fastapi.testclient import TestClient

from app.models.user import User


def test_create_product(client: TestClient, auth_headers: dict, test_user: User):
    """Test creating a product."""
    response = client.post(
        "/api/v1/products",
        json={
            "sku": "SKU-001",
            "name": "Test Product",
            "category": "Electronics",
            "case_pack_quantity": 12,
            "pallet_quantity": 720,
            "net_weight": 10.5,
            "manufacturer": "Acme",
            "description": "Test product description",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "SKU-001"
    assert data["name"] == "Test Product"
    assert data["company_id"] == str(test_user.company_id)
    assert float(data["net_weight"]) == 10.5
    assert data["manufacturer"] == "Acme"
    assert data["classification_count"] == 0


def test_create_product_duplicate_sku_same_company(client: TestClient, auth_headers: dict):
    """Test that duplicate SKU in same company fails."""
    # Create first product
    response1 = client.post(
        "/api/v1/products",
        json={
            "sku": "SKU-001",
            "name": "Product 1",
        },
        headers=auth_headers,
    )
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = client.post(
        "/api/v1/products",
        json={
            "sku": "SKU-001",
            "name": "Product 2",
        },
        headers=auth_headers,
    )

    assert response2.status_code == 409
    assert response2.json()["detail"]["code"] == "PRODUCT_DUPLICATE"


def test_list_products(client: TestClient, auth_headers: dict):
    """Test listing products."""
    # Create some products
    for i in range(3):
        client.post(
            "/api/v1/products",
            json={
                "sku": f"SKU-{i:03d}",
                "name": f"Product {i}",
            },
            headers=auth_headers,
        )

    response = client.get(
        "/api/v1/products",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert all(item["classification_count"] == 0 for item in data["items"])


def test_search_products_by_sku(client: TestClient, auth_headers: dict):
    """Test searching products by SKU."""
    client.post(
        "/api/v1/products",
        json={
            "sku": "SEARCH-001",
            "name": "Searchable Product",
        },
        headers=auth_headers,
    )

    response = client.get(
        "/api/v1/products?search=SEARCH",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["sku"] == "SEARCH-001"


def test_filter_products_by_category(client: TestClient, auth_headers: dict):
    """Test filtering products by category."""
    client.post(
        "/api/v1/products",
        json={
            "sku": "CAT-001",
            "name": "Category Product",
            "category": "Electronics",
        },
        headers=auth_headers,
    )

    response = client.get(
        "/api/v1/products?category=Electronics",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


def test_get_product_detail(client: TestClient, auth_headers: dict):
    """Test getting product details."""
    # Create product
    create_response = client.post(
        "/api/v1/products",
        json={
            "sku": "DETAIL-001",
            "name": "Detail Product",
        },
        headers=auth_headers,
    )
    product_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "DETAIL-001"
    assert data["classifications"] == []
    assert data["packaging"] == []


def test_update_product(client: TestClient, auth_headers: dict):
    """Test updating a product."""
    # Create product
    create_response = client.post(
        "/api/v1/products",
        json={
            "sku": "UPDATE-001",
            "name": "Original Name",
        },
        headers=auth_headers,
    )
    product_id = create_response.json()["id"]

    # Update product
    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Updated Name",
            "category": "New Category",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["category"] == "New Category"


def test_delete_product(client: TestClient, auth_headers: dict):
    """Test deleting a product."""
    # Create product
    create_response = client.post(
        "/api/v1/products",
        json={
            "sku": "DELETE-001",
            "name": "To Delete",
        },
        headers=auth_headers,
    )
    product_id = create_response.json()["id"]

    # Delete product
    response = client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # Verify product is inactive
    get_response = client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False
