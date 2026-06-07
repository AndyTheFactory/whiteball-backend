"""Main API router."""

from fastapi import APIRouter

from app.api.routes import auth, company, packaging, products, users

# Create main router
api_router = APIRouter(prefix="/api/v1")

# Include route modules
api_router.include_router(auth.router)
api_router.include_router(company.router)
api_router.include_router(users.router)
api_router.include_router(products.router)
api_router.include_router(packaging.router)

__all__ = ["api_router"]
