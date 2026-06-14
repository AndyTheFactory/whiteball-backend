"""Tests for classification-specific product element endpoints."""

import uuid

from fastapi.testclient import TestClient


def _create_product(client: TestClient, auth_headers: dict) -> str:
    """Helper to create a test product."""
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


# =====================================================================
# PACKAGING Tests
# =====================================================================


def test_packaging_upsert_creates_elements(client: TestClient, auth_headers: dict):
    """POST /elements/packaging creates packaging elements."""
    product_id = _create_product(client, auth_headers)

    response = client.post(
        f"/api/v1/products/{product_id}/elements/packaging",
        json=[
            {
                "type_code": "primary",
                "material_code": "other_plastics",
                "name": "Bottle",
                "weight_grams": 20.5,
                "grouping": "pallet",
            },
            {
                "type_code": "secondary",
                "material_code": "paper",
                "name": "Box",
                "weight_grams": 100,
                "grouping": "individual",
            },
        ],
        headers=auth_headers,
    )

    assert response.status_code == 201
    items = response.json()
    assert len(items) == 2
    assert items[0]["name"] == "Bottle"
    assert items[0]["grouping"] == "pallet"
    assert items[1]["name"] == "Box"
    assert items[1]["grouping"] == "individual"


def test_packaging_get_returns_elements(client: TestClient, auth_headers: dict):
    """GET /elements/packaging returns all packaging elements."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/packaging",
        json=[
            {
                "type_code": "primary",
                "material_code": "other_plastics",
                "name": "Bottle",
                "weight_grams": 20,
                "grouping": "pallet",
            }
        ],
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/products/{product_id}/elements/packaging",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Bottle"


def test_packaging_delete_removes_all(client: TestClient, auth_headers: dict):
    """DELETE /elements/packaging removes all packaging elements."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/packaging",
        json=[
            {"name": "Item1"},
            {"name": "Item2"},
        ],
        headers=auth_headers,
    )

    response = client.delete(
        f"/api/v1/products/{product_id}/elements/packaging",
        headers=auth_headers,
    )
    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/products/{product_id}/elements/packaging",
        headers=auth_headers,
    )
    assert get_response.json() == []


def test_packaging_upsert_replaces_old(client: TestClient, auth_headers: dict):
    """POST /elements/packaging replaces existing elements."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/packaging",
        json=[{"name": "OldItem"}],
        headers=auth_headers,
    )

    response = client.post(
        f"/api/v1/products/{product_id}/elements/packaging",
        json=[{"name": "NewItem1"}, {"name": "NewItem2"}],
        headers=auth_headers,
    )

    assert response.status_code == 201
    items = response.json()
    assert len(items) == 2
    assert all(item["name"] in ("NewItem1", "NewItem2") for item in items)


# =====================================================================
# SCP Tests
# =====================================================================


def test_scp_upsert_creates_element(client: TestClient, auth_headers: dict):
    """POST /elements/scp creates or replaces SCP element."""
    product_id = _create_product(client, auth_headers)

    response = client.post(
        f"/api/v1/products/{product_id}/elements/scp",
        json={"product_value": 123.45},
        headers=auth_headers,
    )

    assert response.status_code == 201
    items = response.json()
    assert len(items) == 1
    assert float(items[0]["product_value"]) == 123.45


def test_scp_get_returns_element(client: TestClient, auth_headers: dict):
    """GET /elements/scp returns SCP element."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/scp",
        json={"product_value": 50},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/products/{product_id}/elements/scp",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert float(items[0]["product_value"]) == 50


def test_scp_delete_removes_element(client: TestClient, auth_headers: dict):
    """DELETE /elements/scp removes SCP element."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/scp",
        json={"product_value": 100},
        headers=auth_headers,
    )

    response = client.delete(
        f"/api/v1/products/{product_id}/elements/scp",
        headers=auth_headers,
    )
    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/products/{product_id}/elements/scp",
        headers=auth_headers,
    )
    assert get_response.json() == []


# =====================================================================
# TIRE Tests
# =====================================================================


def test_tire_upsert_creates_element(client: TestClient, auth_headers: dict):
    """POST /elements/tire creates tire element."""
    product_id = _create_product(client, auth_headers)

    response = client.post(
        f"/api/v1/products/{product_id}/elements/tire",
        json={"weight_grams": 5000},
        headers=auth_headers,
    )

    assert response.status_code == 201
    items = response.json()
    assert len(items) == 1
    assert float(items[0]["weight_grams"]) == 5000


def test_tire_get_returns_element(client: TestClient, auth_headers: dict):
    """GET /elements/tire returns tire element."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/tire",
        json={"weight_grams": 3500},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/products/{product_id}/elements/tire",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert float(items[0]["weight_grams"]) == 3500


# =====================================================================
# TRANSPORT_PACK Tests
# =====================================================================


def test_transport_pack_upsert_stores_attributes(client: TestClient, auth_headers: dict):
    """POST /elements/transport_pack stores attributes correctly."""
    product_id = _create_product(client, auth_headers)

    response = client.post(
        f"/api/v1/products/{product_id}/elements/transport_pack",
        json={
            "name": "Wrap",
            "material_code": "ldpe",
            "thickness_micron": 25.5,
            "weight_grams": 10,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Wrap"
    assert items[0]["material_code"] == "ldpe"
    assert float(items[0]["thickness_micron"]) == 25.5
    assert float(items[0]["weight_grams"]) == 10


def test_transport_pack_get_returns_element(client: TestClient, auth_headers: dict):
    """GET /elements/transport_pack returns element."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/transport_pack",
        json={
            "name": "Film",
            "material_code": "pe",
            "thickness_micron": 50,
            "weight_grams": 15,
        },
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/products/{product_id}/elements/transport_pack",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Film"


# =====================================================================
# OIL Tests
# =====================================================================


def test_oil_upsert_stores_attributes(client: TestClient, auth_headers: dict):
    """POST /elements/oil stores quantity and measure_unit."""
    product_id = _create_product(client, auth_headers)

    response = client.post(
        f"/api/v1/products/{product_id}/elements/oil",
        json={"quantity": 500, "measure_unit": "ml"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    items = response.json()
    assert len(items) == 1
    assert float(items[0]["quantity"]) == 500
    assert items[0]["measure_unit"] == "ml"


def test_oil_get_returns_element(client: TestClient, auth_headers: dict):
    """GET /elements/oil returns element."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/oil",
        json={"quantity": 1000, "measure_unit": "liters"},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/products/{product_id}/elements/oil",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert float(items[0]["quantity"]) == 1000


# =====================================================================
# EEE Tests
# =====================================================================


def test_eee_upsert_stores_dimensions(client: TestClient, auth_headers: dict):
    """POST /elements/eee stores dimensions and category."""
    product_id = _create_product(client, auth_headers)

    response = client.post(
        f"/api/v1/products/{product_id}/elements/eee",
        json={
            "height_mm": 150,
            "width_mm": 100,
            "depth_mm": 50,
            "weight_grams": 500,
            "category_code": "cat1",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    items = response.json()
    assert len(items) == 1
    assert float(items[0]["height_mm"]) == 150
    assert float(items[0]["width_mm"]) == 100
    assert items[0]["category_code"] == "cat1"
    assert float(items[0]["weight_grams"]) == 500


def test_eee_get_returns_element(client: TestClient, auth_headers: dict):
    """GET /elements/eee returns element."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/eee",
        json={"height_mm": 200, "category_code": "cat2"},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/products/{product_id}/elements/eee",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert float(items[0]["height_mm"]) == 200


# =====================================================================
# BATTERIES Tests
# =====================================================================


def test_batteries_upsert_stores_composition(client: TestClient, auth_headers: dict):
    """POST /elements/batteries stores composition and category."""
    product_id = _create_product(client, auth_headers)

    response = client.post(
        f"/api/v1/products/{product_id}/elements/batteries",
        json={
            "chemical_composition_code": "li_ion",
            "weight_grams": 250,
            "category_code": "primary",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    items = response.json()
    assert len(items) == 1
    assert items[0]["chemical_composition_code"] == "li_ion"
    assert items[0]["category_code"] == "primary"
    assert float(items[0]["weight_grams"]) == 250


def test_batteries_get_returns_element(client: TestClient, auth_headers: dict):
    """GET /elements/batteries returns element."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/batteries",
        json={"chemical_composition_code": "ni_mh", "weight_grams": 150},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/products/{product_id}/elements/batteries",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["chemical_composition_code"] == "ni_mh"


# =====================================================================
# SGR Tests
# =====================================================================


def test_sgr_upsert_stores_dimensions_and_properties(client: TestClient, auth_headers: dict):
    """POST /elements/sgr stores all SGR fields."""
    product_id = _create_product(client, auth_headers)

    response = client.post(
        f"/api/v1/products/{product_id}/elements/sgr",
        json={
            "material_code": "glass",
            "color_code": "amber",
            "has_uv_protection": True,
            "volume_ml": 750,
            "height_wo_cap_mm": 250,
            "height_w_cap_mm": 260,
            "diameter_mm": 80,
            "weight_grams": 600,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    items = response.json()
    assert len(items) == 1
    assert items[0]["material_code"] == "glass"
    assert items[0]["color_code"] == "amber"
    assert items[0]["has_uv_protection"] is True
    assert float(items[0]["volume_ml"]) == 750
    assert float(items[0]["height_wo_cap_mm"]) == 250
    assert float(items[0]["height_w_cap_mm"]) == 260
    assert float(items[0]["diameter_mm"]) == 80
    assert float(items[0]["weight_grams"]) == 600


def test_sgr_get_returns_element(client: TestClient, auth_headers: dict):
    """GET /elements/sgr returns element."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/sgr",
        json={
            "material_code": "plastic",
            "color_code": "clear",
            "has_uv_protection": False,
            "volume_ml": 500,
            "weight_grams": 50,
        },
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/products/{product_id}/elements/sgr",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["material_code"] == "plastic"
    assert items[0]["has_uv_protection"] is False


# =====================================================================
# SUP Tests
# =====================================================================


def test_sup_upsert_stores_composition(client: TestClient, auth_headers: dict):
    """POST /elements/sup stores composition percentages."""
    product_id = _create_product(client, auth_headers)

    response = client.post(
        f"/api/v1/products/{product_id}/elements/sup",
        json={
            "composition_code": "mixed",
            "percentage_plastic": 70.5,
            "percentage_RPET": 29.5,
            "weight_grams": 100,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    items = response.json()
    assert len(items) == 1
    assert items[0]["composition_code"] == "mixed"
    assert float(items[0]["percentage_plastic"]) == 70.5
    assert float(items[0]["percentage_RPET"]) == 29.5
    assert float(items[0]["weight_grams"]) == 100


def test_sup_get_returns_element(client: TestClient, auth_headers: dict):
    """GET /elements/sup returns element."""
    product_id = _create_product(client, auth_headers)

    client.post(
        f"/api/v1/products/{product_id}/elements/sup",
        json={
            "composition_code": "pure",
            "percentage_plastic": 100,
            "percentage_RPET": 0,
        },
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/products/{product_id}/elements/sup",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["composition_code"] == "pure"


# =====================================================================
# Cross-Classification Tests
# =====================================================================


def test_multiple_classifications_coexist(client: TestClient, auth_headers: dict):
    """Different classifications can coexist for the same product."""
    product_id = _create_product(client, auth_headers)

    # Create packaging
    client.post(
        f"/api/v1/products/{product_id}/elements/packaging",
        json=[{"name": "Box", "weight_grams": 50}],
        headers=auth_headers,
    )

    # Create SCP
    client.post(
        f"/api/v1/products/{product_id}/elements/scp",
        json={"product_value": 100},
        headers=auth_headers,
    )

    # Verify both exist
    packaging = client.get(
        f"/api/v1/products/{product_id}/elements/packaging",
        headers=auth_headers,
    ).json()
    scp = client.get(
        f"/api/v1/products/{product_id}/elements/scp",
        headers=auth_headers,
    ).json()

    assert len(packaging) == 1
    assert len(scp) == 1


def test_deleting_one_classification_doesnt_affect_others(client: TestClient, auth_headers: dict):
    """Deleting one classification doesn't affect others."""
    product_id = _create_product(client, auth_headers)

    # Create two classifications
    client.post(
        f"/api/v1/products/{product_id}/elements/tire",
        json={"weight_grams": 1000},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/products/{product_id}/elements/eee",
        json={"height_mm": 100},
        headers=auth_headers,
    )

    # Delete tire
    client.delete(
        f"/api/v1/products/{product_id}/elements/tire",
        headers=auth_headers,
    )

    # Verify tire is gone but eee remains
    tire = client.get(
        f"/api/v1/products/{product_id}/elements/tire",
        headers=auth_headers,
    ).json()
    eee = client.get(
        f"/api/v1/products/{product_id}/elements/eee",
        headers=auth_headers,
    ).json()

    assert len(tire) == 0
    assert len(eee) == 1


def test_get_empty_classification_returns_empty_list(client: TestClient, auth_headers: dict):
    """GET on non-existent classification returns empty list."""
    product_id = _create_product(client, auth_headers)

    response = client.get(
        f"/api/v1/products/{product_id}/elements/packaging",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_delete_empty_classification_succeeds(client: TestClient, auth_headers: dict):
    """DELETE on empty classification succeeds."""
    product_id = _create_product(client, auth_headers)

    response = client.delete(
        f"/api/v1/products/{product_id}/elements/scp",
        headers=auth_headers,
    )

    assert response.status_code == 204


def test_product_not_found_returns_404(client: TestClient, auth_headers: dict):
    """Accessing elements for non-existent product returns 404."""
    fake_product_id = uuid.uuid4()

    response = client.post(
        f"/api/v1/products/{fake_product_id}/elements/packaging",
        json=[{"name": "Test"}],
        headers=auth_headers,
    )

    assert response.status_code == 404
