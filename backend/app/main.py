"""
Application entry point for OpenOps AI backend.
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.api.router import api_router
from app.api.v1.auth import router as auth_router
from app.core.logging import configure_logging


def create_app():
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    configure_logging()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(api_router, prefix="/api")
    app.include_router(auth_router, prefix="/api/auth")
    
    @app.on_event("startup")
    async def startup_event():
        """Application startup."""
        # from app.core.dependencies import setup_dependencies
        # await setup_dependencies()
        
        from app.core.config import get_settings
        from app.infrastructure.demo_seed import seed_demo_data
        
        settings = get_settings()
        if settings.SEED_DEMO_DATA:
            await seed_demo_data()
    
    return app


app = create_app()