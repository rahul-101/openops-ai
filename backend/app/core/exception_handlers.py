from fastapi import Request
from fastapi.responses import JSONResponse

from app.api.models.api_response import ApiResponse
from app.core.exceptions import OpenOpsException


async def openops_exception_handler(
    request: Request,
    exc: OpenOpsException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            success=False,
            message=exc.message,
            data=None,
        ).model_dump(),
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            success=False,
            message="Internal Server Error",
            data=None,
        ).model_dump(),
    )