"""Packaging routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.exceptions import NotFoundException, ValidationException
from app.models.packaging import PackagingItem
from app.models.product import Product
from app.models.product_packaging_association import ProductPackagingAssociation
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.packaging import (
    PackagingAssociationResponse,
    PackagingAssociationUpdate,
    PackagingItemCreate,
    PackagingItemResponse,
    PackagingItemUpdate,
    ProductPackagingInput,
)

router = APIRouter(tags=["packaging"])


@router.get("/packaging-items", response_model=PaginatedResponse)
async def list_packaging_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str | None = Query(None),
    type_filter: str | None = Query(None, alias="type"),
    subtype: str | None = Query(None),
    material: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse:
    """List packaging items for the current company."""
    stmt = select(PackagingItem).where(PackagingItem.company_id == current_user.company_id)

    if search:
        stmt = stmt.where((PackagingItem.name.ilike(f"%{search}%")) | (PackagingItem.material.ilike(f"%{search}%")))

    if type_filter:
        stmt = stmt.where(PackagingItem.type.ilike(f"%{type_filter}%"))

    if subtype:
        stmt = stmt.where(PackagingItem.subtype.ilike(f"%{subtype}%"))

    if material:
        stmt = stmt.where(PackagingItem.material.ilike(f"%{material}%"))

    count_stmt = (
        select(func.count()).select_from(PackagingItem).where(PackagingItem.company_id == current_user.company_id)
    )
    total = db.execute(count_stmt).scalar() or 0

    stmt = stmt.limit(limit).offset(offset)
    items = db.execute(stmt).scalars().all()

    return PaginatedResponse(
        items=[PackagingItemResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/packaging-items", response_model=PackagingItemResponse, status_code=status.HTTP_201_CREATED)
async def create_packaging_item(
    item_data: PackagingItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackagingItemResponse:
    """Create a new packaging item."""
    item = PackagingItem(company_id=current_user.company_id, **item_data.model_dump())

    db.add(item)
    db.commit()
    db.refresh(item)

    return PackagingItemResponse.model_validate(item)


@router.patch("/packaging-items/{item_id}", response_model=PackagingItemResponse)
async def update_packaging_item(
    item_id: UUID,
    item_data: PackagingItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackagingItemResponse:
    """Update a packaging item."""
    stmt = select(PackagingItem).where(
        (PackagingItem.id == item_id) & (PackagingItem.company_id == current_user.company_id)
    )
    item = db.execute(stmt).scalars().first()

    if not item:
        raise NotFoundException("Packaging item")

    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    return PackagingItemResponse.model_validate(item)


@router.delete("/packaging-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_packaging_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a packaging item and all its associations."""
    stmt = select(PackagingItem).where(
        (PackagingItem.id == item_id) & (PackagingItem.company_id == current_user.company_id)
    )
    item = db.execute(stmt).scalars().first()

    if not item:
        raise NotFoundException("Packaging item")

    # Delete all associations
    stmt = select(ProductPackagingAssociation).where(ProductPackagingAssociation.packaging_item_id == item_id)
    associations = db.execute(stmt).scalars().all()
    for assoc in associations:
        db.delete(assoc)

    db.delete(item)
    db.commit()


@router.post(
    "/products/{product_id}/packaging", response_model=PackagingAssociationResponse, status_code=status.HTTP_201_CREATED
)
async def associate_packaging_with_product(
    product_id: UUID,
    association_data: ProductPackagingInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackagingAssociationResponse:
    """Associate packaging with a product."""
    # Verify product exists and belongs to user's company
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    packaging_item_id = association_data.packaging_item_id

    # If creating new packaging item
    if association_data.packaging_item:
        if association_data.packaging_item_id:
            raise ValidationException("Cannot specify both packaging_item_id and packaging_item")

        new_item = PackagingItem(company_id=current_user.company_id, **association_data.packaging_item.model_dump())
        db.add(new_item)
        db.flush()
        packaging_item_id = new_item.id

    if not packaging_item_id:
        raise ValidationException("Must specify either packaging_item_id or packaging_item")

    # Verify packaging item exists and belongs to user's company
    stmt = select(PackagingItem).where(
        (PackagingItem.id == packaging_item_id) & (PackagingItem.company_id == current_user.company_id)
    )
    packaging_item = db.execute(stmt).scalars().first()

    if not packaging_item:
        raise NotFoundException("Packaging item")

    # Create association
    association = ProductPackagingAssociation(
        product_id=product_id,
        packaging_item_id=packaging_item_id,
        quantity_per_product_unit=association_data.quantity_per_product_unit,
        applies_to_unit=association_data.applies_to_unit,
        notes=association_data.notes,
    )

    db.add(association)
    db.commit()
    db.refresh(association)

    return PackagingAssociationResponse(
        association_id=association.id,
        packaging_item_id=association.packaging_item.id,
        type=association.packaging_item.type,
        subtype=association.packaging_item.subtype,
        material=association.packaging_item.material,
        name=association.packaging_item.name,
        weight_grams=association.packaging_item.weight_grams,
        quantity_per_product_unit=association.quantity_per_product_unit,
        applies_to_unit=association.applies_to_unit,
        notes=association.notes,
    )


@router.patch("/products/{product_id}/packaging/{association_id}", response_model=PackagingAssociationResponse)
async def update_product_packaging_association(
    product_id: UUID,
    association_id: UUID,
    association_data: PackagingAssociationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PackagingAssociationResponse:
    """Update a product packaging association."""
    # Verify product exists
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    # Verify association exists
    stmt = select(ProductPackagingAssociation).where(ProductPackagingAssociation.id == association_id)
    association = db.execute(stmt).scalars().first()

    if not association or association.product_id != product_id:
        raise NotFoundException("Product packaging association")

    # Update association fields
    if association_data.quantity_per_product_unit is not None:
        association.quantity_per_product_unit = association_data.quantity_per_product_unit

    if association_data.applies_to_unit is not None:
        association.applies_to_unit = association_data.applies_to_unit

    if association_data.notes is not None:
        association.notes = association_data.notes

    # Update packaging item if provided
    if association_data.packaging_item:
        packaging_item = association.packaging_item
        update_data = association_data.packaging_item.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(packaging_item, field, value)

    db.commit()
    db.refresh(association)

    return PackagingAssociationResponse(
        association_id=association.id,
        packaging_item_id=association.packaging_item.id,
        type=association.packaging_item.type,
        subtype=association.packaging_item.subtype,
        material=association.packaging_item.material,
        name=association.packaging_item.name,
        weight_grams=association.packaging_item.weight_grams,
        quantity_per_product_unit=association.quantity_per_product_unit,
        applies_to_unit=association.applies_to_unit,
        notes=association.notes,
    )


@router.delete("/products/{product_id}/packaging/{association_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_packaging_from_product(
    product_id: UUID,
    association_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove a packaging association from a product."""
    # Verify product exists
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    # Verify and delete association
    stmt = select(ProductPackagingAssociation).where(ProductPackagingAssociation.id == association_id)
    association = db.execute(stmt).scalars().first()

    if not association or association.product_id != product_id:
        raise NotFoundException("Product packaging association")

    db.delete(association)
    db.commit()
