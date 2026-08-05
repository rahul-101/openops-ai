"""
Backend entry point for OpenOps AI.
"""

import uvicorn
from app.main import app
from app.core.config import get_settings


def main():
    """Main entry point for the backend."""
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()