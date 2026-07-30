import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger
from app.core.request_context import request_id_ctx


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        request_id = str(uuid.uuid4())

        token = request_id_ctx.set(request_id)

        start_time = time.perf_counter()

        try:
            response = await call_next(request)

            process_time = (time.perf_counter() - start_time) * 1000

            logger.bind(request_id=request_id).info(
                "HTTP Request",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time_ms=round(process_time, 2),
            )

            response.headers["X-Request-ID"] = request_id

            return response

        finally:
            request_id_ctx.reset(token)