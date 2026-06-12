"""Product routes."""

from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.routes.packaging import _classification_response, _require_dictionary_value
from app.core.exceptions import DuplicateException, NotFoundException
from app.models.product import Product
from app.models.product_packaging_association import ProductClassification
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.packaging import (
    ProductClassificationCreate,
    ProductClassificationResponse,
    ProductClassificationUpdate,
)
from app.schemas.product import ProductCreate, ProductDetailResponse, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/categories", response_model=list[str])
async def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prefix: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
) -> list[str]:
    """List distinct product categories for the current company, optionally filtered by prefix."""
    stmt = (
        select(Product.category)
        .where(Product.company_id == current_user.company_id)
        .where(Product.category.isnot(None))
        .where(Product.category != "")
        .distinct()
    )

    if prefix:
        stmt = stmt.where(Product.category.ilike(f"{prefix}%"))

    stmt = stmt.order_by(Product.category).limit(limit)

    rows = cast(list[str], list(db.execute(stmt).scalars().all()))

    return rows


@router.get("", response_model=PaginatedResponse)
async def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str | None = Query(None),
    category: str | None = Query(None),
    is_active: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("name", pattern="^(name|sku|created_at)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
) -> PaginatedResponse:
    """List products for the current company."""
    # Build query
    stmt = select(Product).where(Product.company_id == current_user.company_id)

    # Apply filters
    if search:
        stmt = stmt.where((Product.sku.ilike(f"%{search}%")) | (Product.name.ilike(f"%{search}%")))

    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))

    if is_active is not None:
        stmt = stmt.where(Product.is_active == is_active)

    # Count total
    count_stmt = select(func.count()).select_from(Product).where(Product.company_id == current_user.company_id)
    if search:
        count_stmt = count_stmt.where((Product.sku.ilike(f"%{search}%")) | (Product.name.ilike(f"%{search}%")))
    if category:
        count_stmt = count_stmt.where(Product.category.ilike(f"%{category}%"))
    if is_active is not None:
        count_stmt = count_stmt.where(Product.is_active == is_active)

    total = db.execute(count_stmt).scalar() or 0

    # Apply sorting
    if sort_order == "desc":
        stmt = stmt.order_by(getattr(Product, sort_by).desc())
    else:
        stmt = stmt.order_by(getattr(Product, sort_by))

    # Apply pagination
    stmt = stmt.limit(limit).offset(offset)

    products = db.execute(stmt).scalars().all()

    items = [
        ProductResponse(
            **{
                **product.__dict__,
                "packaging_count": len(product.classifications),
                "classification_count": len(product.classifications),
            }
        )
        for product in products
    ]

    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    """Create a new product."""
    # Check if SKU already exists for this company
    stmt = select(Product).where((Product.company_id == current_user.company_id) & (Product.sku == product_data.sku))
    existing = db.execute(stmt).scalars().first()

    if existing:
        raise DuplicateException("product", "SKU")

    # Create product
    product = Product(company_id=current_user.company_id, **product_data.model_dump())

    db.add(product)
    db.commit()
    db.refresh(product)

    return ProductResponse(
        **{
            **product.__dict__,
            "packaging_count": len(product.classifications),
            "classification_count": len(product.classifications),
        }
    )


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductDetailResponse:
    """Get product details with associated packaging."""
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    # Format packaging data
    classifications = [assoc.classification_code for assoc in product.classifications]

    return ProductDetailResponse(
        **{
            **product.__dict__,
            "packaging_count": len(classifications),
            "classification_count": len(classifications),
            "packaging": classifications,
            "classifications": classifications,
        }
    )


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    """Update a product."""
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    # Check for duplicate SKU if SKU is being updated
    if product_data.sku and product_data.sku != product.sku:
        stmt = select(Product).where(
            (Product.company_id == current_user.company_id) & (Product.sku == product_data.sku)
        )
        existing = db.execute(stmt).scalars().first()

        if existing:
            raise DuplicateException("product", "SKU")

    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return ProductResponse(
        **{
            **product.__dict__,
            "packaging_count": len(product.classifications),
            "classification_count": len(product.classifications),
        }
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Soft delete a product (set is_active to False)."""
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    product.is_active = False
    db.commit()


@router.get("/{product_id}/classifications", response_model=list[ProductClassificationResponse])
async def list_product_classifications(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProductClassificationResponse]:
    """List classifications for a product."""
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    return [_classification_response(db, classification) for classification in product.classifications]


@router.post(
    "/{product_id}/classifications",
    response_model=ProductClassificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_classification(
    product_id: UUID,
    classification_data: ProductClassificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductClassificationResponse:
    """Create a product classification."""
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    _require_dictionary_value(db, classification_data.classification_code, "classification_code")

    existing = (
        db.execute(
            select(ProductClassification).where(
                (ProductClassification.product_id == product_id)
                & (ProductClassification.classification_code == classification_data.classification_code)
            )
        )
        .scalars()
        .first()
    )
    if existing:
        raise DuplicateException("product classification", "classification code")

    association = ProductClassification(
        product_id=product_id, classification_code=classification_data.classification_code
    )
    db.add(association)
    db.commit()
    db.refresh(association)

    return _classification_response(db, association)


@router.patch("/{product_id}/classifications/{association_id}", response_model=ProductClassificationResponse)
async def update_product_classification(
    product_id: UUID,
    association_id: UUID,
    classification_data: ProductClassificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductClassificationResponse:
    """Update a product classification."""
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    association = (
        db.execute(select(ProductClassification).where(ProductClassification.id == association_id)).scalars().first()
    )
    if not association or association.product_id != product_id:
        raise NotFoundException("Product classification")

    update_data = classification_data.model_dump(exclude_unset=True)
    if "classification_code" in update_data:
        _require_dictionary_value(db, update_data["classification_code"], "classification_code")
        association.classification_code = update_data["classification_code"]

    db.commit()
    db.refresh(association)

    return _classification_response(db, association)


@router.delete("/{product_id}/classifications/{association_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product_classification(
    product_id: UUID,
    association_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove a classification from a product."""
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    association = (
        db.execute(select(ProductClassification).where(ProductClassification.id == association_id)).scalars().first()
    )
    if not association or association.product_id != product_id:
        raise NotFoundException("Product classification")

    db.delete(association)
    db.commit()
