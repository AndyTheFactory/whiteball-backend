"""FastAPI application factory."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.config import get_settings
from app.api.router import api_router
from app.db import Base, engine

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Whiteball Backend",
        description="Backend API for Whiteball packaging reporting platform",
        version="0.1.0",
    )
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}
    
    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title="Whiteball Backend API",
            version="0.1.0",
            description="API for managing products and packaging in Whiteball platform",
            routes=app.routes,
        )
        
        openapi_schema["info"]["x-logo"] = {
            "url": "https://whiteball.local/logo.png"
        }
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    return app
