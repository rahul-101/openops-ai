from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.core.middleware import RequestLoggingMiddleware
from app.core.exception_handlers import (
    generic_exception_handler,
    openops_exception_handler,
)
from app.core.exceptions import OpenOpsException

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the application starts and once when it shuts down.
    """

    configure_logging()

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
app.add_exception_handler(
    OpenOpsException,
    openops_exception_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)

app.add_middleware(RequestLoggingMiddleware)
app.include_router(api_router)