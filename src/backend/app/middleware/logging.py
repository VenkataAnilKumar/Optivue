import json
import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def get_correlation_id() -> str:
    """Return the current request correlation ID."""
    return correlation_id_var.get()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """JSON-structured request/response logging middleware."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        log_record = {
            "correlation_id": correlation_id,
            "user_sub": request.headers.get("x-user-sub", "anonymous"),
            "role": request.headers.get("x-user-role", "unknown"),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }
        logger.info(json.dumps(log_record))
        response.headers["X-Correlation-ID"] = correlation_id
        return response
