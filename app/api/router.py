"""Main API router."""

from fastapi import APIRouter

from app.api.routes import auth, company, dictionaries, products, reference, users

# Create main router
api_router = APIRouter(prefix="/api/v1")

# Include route modules
api_router.include_router(auth.router)
api_router.include_router(company.router)
api_router.include_router(users.router)
api_router.include_router(products.router)
api_router.include_router(reference.router)
api_router.include_router(dictionaries.router)

__all__ = ["api_router"]
