"""Dictionary route tests."""

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.dictionary import DictionaryType, DictionaryValue


def test_list_dictionary_values_sorted_by_sort_order(client: TestClient, db: Session):
    """Test listing dictionary values sorted by sort_order."""
    db.add(DictionaryType(id=uuid.uuid4(), code="packaging_materials", name="Packaging Materials"))
    db.add_all(
        [
            DictionaryValue(
                id=uuid.uuid4(),
                dictionary_type_code="packaging_materials",
                code="paper",
                name_ro="Hartie",
                name_en="Paper",
                is_active=True,
                sort_order=20,
            ),
            DictionaryValue(
                id=uuid.uuid4(),
                dictionary_type_code="packaging_materials",
                code="plastic",
                name_ro="Plastic",
                name_en="Plastic",
                is_active=True,
                sort_order=10,
            ),
            DictionaryValue(
                id=uuid.uuid4(),
                dictionary_type_code="packaging_materials",
                code="metal",
                name_ro="Metal",
                name_en="Metal",
                is_active=False,
                sort_order=10,
            ),
        ]
    )
    db.commit()

    response = client.get("/api/v1/dictionaries/packaging_materials/values")

    assert response.status_code == 200
    data = response.json()
    assert [item["code"] for item in data] == ["metal", "plastic", "paper"]
    assert [item["sort_order"] for item in data] == [10, 10, 20]
