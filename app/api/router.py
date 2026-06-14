"""Main API router."""

from fastapi import APIRouter

from app.api.routes import (
    auth,
    classification_elements,
    company,
    dictionaries,
    product_elements,
    products,
    products_classification,
    reference,
    users,
)

# Create main router
api_router = APIRouter(prefix="/api/v1")

# Include route modules
api_router.include_router(auth.router)
api_router.include_router(company.router)
api_router.include_router(users.router)
api_router.include_router(products.router)
api_router.include_router(products_classification.router)
# classification_elements must come before product_elements so the literal
# classification path segments (e.g. /elements/packaging) are not shadowed by
# the generic /{item_id} parameter route.
api_router.include_router(classification_elements.router)
api_router.include_router(product_elements.router)
api_router.include_router(reference.router)
api_router.include_router(dictionaries.router)


__all__ = ["api_router"]
