"""Product element routes scoped to a specific product."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.routes.packaging import _require_dictionary_value
from app.core.exceptions import NotFoundException
from app.models.packaging import PackagingItem
from app.models.product import Product
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.packaging import ProductElementCreate, ProductElementResponse, ProductElementUpdate

router = APIRouter(prefix="/products", tags=["product-elements"])


def _get_owned_product(db: Session, product_id: UUID, current_user: User) -> Product:
    """Return product only if it belongs to the authenticated user's company."""
    product = (
        db.execute(select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id)))
        .scalars()
        .first()
    )
    if not product:
        raise NotFoundException("Product")
    return product


@router.get("/{product_id}/elements", response_model=PaginatedResponse)
async def list_product_elements(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    classification_code: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse:
    """List product elements for a product, optionally filtered by classification code."""
    _get_owned_product(db, product_id, current_user)

    stmt = select(PackagingItem).where(PackagingItem.product_id == product_id)
    count_stmt = select(func.count()).select_from(PackagingItem).where(PackagingItem.product_id == product_id)

    if classification_code:
        stmt = stmt.where(PackagingItem.classification_code == classification_code)
        count_stmt = count_stmt.where(PackagingItem.classification_code == classification_code)

    total = db.execute(count_stmt).scalar() or 0
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()

    return PaginatedResponse(
        items=[ProductElementResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/{product_id}/elements", response_model=ProductElementResponse, status_code=status.HTTP_201_CREATED)
async def create_product_element(
    product_id: UUID,
    item_data: ProductElementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductElementResponse:
    """Create a product element for a product owned by the current user's company."""
    _get_owned_product(db, product_id, current_user)

    _require_dictionary_value(db, item_data.classification_code, "classification_code")
    if item_data.type_code:
        _require_dictionary_value(db, item_data.type_code, "type_code")
    _require_dictionary_value(db, item_data.material_code, "material_code")

    item = PackagingItem(
        company_id=current_user.company_id,
        product_id=product_id,
        **item_data.model_dump(),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return ProductElementResponse.model_validate(item)


@router.patch("/{product_id}/elements/{item_id}", response_model=ProductElementResponse)
async def update_product_element(
    product_id: UUID,
    item_id: UUID,
    item_data: ProductElementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    classification_code: str = Query(..., min_length=1),
) -> ProductElementResponse:
    """Update a product element using a required classification code guard."""
    _get_owned_product(db, product_id, current_user)

    item = (
        db.execute(
            select(PackagingItem).where(
                (PackagingItem.id == item_id)
                & (PackagingItem.product_id == product_id)
                & (PackagingItem.classification_code == classification_code)
            )
        )
        .scalars()
        .first()
    )

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


@router.delete("/{product_id}/elements", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_elements_by_classification(
    product_id: UUID,
    classification_code: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete all product elements for a product and classification code."""
    _get_owned_product(db, product_id, current_user)

    items = (
        db.execute(
            select(PackagingItem).where(
                (PackagingItem.product_id == product_id) & (PackagingItem.classification_code == classification_code)
            )
        )
        .scalars()
        .all()
    )

    for item in items:
        db.delete(item)

    db.commit()
