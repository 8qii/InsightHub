import logging
import re
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint

logger = logging.getLogger("insighthub.http")

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def get_request_id(request: Request) -> str:
    incoming_request_id = request.headers.get(REQUEST_ID_HEADER)
    if incoming_request_id and REQUEST_ID_PATTERN.fullmatch(incoming_request_id):
        return incoming_request_id
    return str(uuid.uuid4())


async def request_id_logging_middleware(
    request: Request, call_next: RequestResponseEndpoint
) -> Response:
    request_id = get_request_id(request)
    request.state.request_id = request_id
    started_at = time.perf_counter()
    response = await call_next(request)
    response.headers[REQUEST_ID_HEADER] = request_id
    logger.info(
        "HTTP request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
        },
    )
    return response
