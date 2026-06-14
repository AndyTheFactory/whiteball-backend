from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.exceptions import DuplicateException, NotFoundException, ValidationException
from app.models import DictionaryValue
from app.models.product import Product
from app.models.product_classification import ProductClassification
from app.models.user import User
from app.schemas.packaging import (
    ProductClassificationCreate,
    ProductClassificationResponse,
    ProductClassificationUpdate,
)

router = APIRouter(prefix="/products", tags=["Product Classification"])


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


@router.delete("/{product_id}/classifications/all", status_code=status.HTTP_204_NO_CONTENT)
async def remove_all_product_classifications(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove all classifications from a product."""
    stmt = select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id))
    product = db.execute(stmt).scalars().first()

    if not product:
        raise NotFoundException("Product")

    associations = (
        db.execute(select(ProductClassification).where(ProductClassification.product_id == product_id)).scalars().all()
    )
    for association in associations:
        db.delete(association)
    db.commit()


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
