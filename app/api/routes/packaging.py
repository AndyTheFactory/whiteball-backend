"""Packaging routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.exceptions import NotFoundException, ValidationException
from app.models.dictionary import DictionaryValue
from app.models.packaging import PackagingItem
from app.models.product_packaging_association import ProductClassification
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.packaging import (
    ProductClassificationResponse,
    ProductElementCreate,
    ProductElementResponse,
    ProductElementUpdate,
)

router = APIRouter(tags=["packaging"])


def _require_dictionary_value(db: Session, code: str, dictionary_type_code: str) -> DictionaryValue:
    value = (
        db.execute(
            select(DictionaryValue).where(
                (DictionaryValue.code == code) & (DictionaryValue.dictionary_type_code == dictionary_type_code)
            )
        )
        .scalars()
        .first()
    )

    if not value:
        raise ValidationException(f"Unknown {dictionary_type_code.replace('_', ' ')}: {code}")

    return value


def _classification_response(db: Session, association: ProductClassification) -> ProductClassificationResponse:
    value = (
        db.execute(select(DictionaryValue).where(DictionaryValue.code == association.classification_code))
        .scalars()
        .first()
    )
    return ProductClassificationResponse(
        association_id=association.id,
        product_id=association.product_id,
        classification_code=association.classification_code,
        name_ro=value.name_ro if value else None,
        name_en=value.name_en if value else None,
        is_active=value.is_active if value else None,
    )


@router.get("/product-elements", response_model=PaginatedResponse)
@router.get("/packaging-items", response_model=PaginatedResponse)
async def list_product_elements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str | None = Query(None),
    classification_code: str | None = Query(None),
    type_code: str | None = Query(None, alias="type"),
    material_code: str | None = Query(None, alias="material"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse:
    """List product elements for the current company."""
    stmt = select(PackagingItem).where(PackagingItem.company_id == current_user.company_id)

    if search:
        stmt = stmt.where((PackagingItem.name.ilike(f"%{search}%")) | (PackagingItem.description.ilike(f"%{search}%")))

    if classification_code:
        stmt = stmt.where(PackagingItem.classification_code == classification_code)

    if type_code:
        stmt = stmt.where(PackagingItem.type_code == type_code)

    if material_code:
        stmt = stmt.where(PackagingItem.material_code == material_code)

    count_stmt = (
        select(func.count()).select_from(PackagingItem).where(PackagingItem.company_id == current_user.company_id)
    )
    if search:
        count_stmt = count_stmt.where(
            (PackagingItem.name.ilike(f"%{search}%")) | (PackagingItem.description.ilike(f"%{search}%"))
        )
    if classification_code:
        count_stmt = count_stmt.where(PackagingItem.classification_code == classification_code)
    if type_code:
        count_stmt = count_stmt.where(PackagingItem.type_code == type_code)
    if material_code:
        count_stmt = count_stmt.where(PackagingItem.material_code == material_code)

    total = db.execute(count_stmt).scalar() or 0
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()

    return PaginatedResponse(
        items=[ProductElementResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/product-elements", response_model=ProductElementResponse, status_code=status.HTTP_201_CREATED)
@router.post("/packaging-items", response_model=ProductElementResponse, status_code=status.HTTP_201_CREATED)
async def create_product_element(
    item_data: ProductElementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductElementResponse:
    """Create a new product element."""
    _require_dictionary_value(db, item_data.classification_code, "classification_code")
    if item_data.type_code:
        _require_dictionary_value(db, item_data.type_code, "type_code")
    _require_dictionary_value(db, item_data.material_code, "material_code")

    item = PackagingItem(company_id=current_user.company_id, **item_data.model_dump())

    db.add(item)
    db.commit()
    db.refresh(item)

    return ProductElementResponse.model_validate(item)


@router.patch("/product-elements/{item_id}", response_model=ProductElementResponse)
@router.patch("/packaging-items/{item_id}", response_model=ProductElementResponse)
async def update_product_element(
    item_id: UUID,
    item_data: ProductElementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductElementResponse:
    """Update a product element."""
    stmt = select(PackagingItem).where(
        (PackagingItem.id == item_id) & (PackagingItem.company_id == current_user.company_id)
    )
    item = db.execute(stmt).scalars().first()

    if not item:
        raise NotFoundException("Product element")

    update_data = item_data.model_dump(exclude_unset=True)
    if "classification_code" in update_data:
        _require_dictionary_value(db, update_data["classification_code"], "classification_code")
    if "type_code" in update_data and update_data["type_code"] is not None:
        _require_dictionary_value(db, update_data["type_code"], "type_code")
    if "material_code" in update_data:
        _require_dictionary_value(db, update_data["material_code"], "material_code")

    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    return ProductElementResponse.model_validate(item)


@router.delete("/product-elements/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/packaging-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_element(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a product element."""
    item_stmt = select(PackagingItem).where(
        (PackagingItem.id == item_id) & (PackagingItem.company_id == current_user.company_id)
    )
    item = db.execute(item_stmt).scalars().first()

    if not item:
        raise NotFoundException("Product element")

    db.delete(item)
    db.commit()
