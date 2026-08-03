from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging, logger
from app.core.middleware import RequestLoggingMiddleware
from app.infrastructure.dependencies import get_provider_bootstrap
from app.infrastructure.demo_seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the application starts and once when it shuts down.
    """

    configure_logging()

    get_provider_bootstrap().run()

    if settings.SEED_DEMO_DATA:
        await seed_demo_data()

    logger.info(
        "Application started",
        application=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
    )

    yield

    logger.info("Application stopped")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Autonomous Incident Response Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Register all global exception handlers
register_exception_handlers(app)

# Register middleware
app.add_middleware(RequestLoggingMiddleware)

# Register API routes
app.include_router(api_router)
