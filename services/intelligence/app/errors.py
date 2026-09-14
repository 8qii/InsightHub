import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """A known, safe-to-display application error."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


def error_response(status_code: int, code: str, message: str, request: Request) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    body: dict[str, Any] = {
        "error": {"code": code, "message": message, "request_id": request_id}
    }
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, _exception: RequestValidationError
    ) -> JSONResponse:
        return error_response(422, "validation_error", "Request validation failed.", request)

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exception: AppError) -> JSONResponse:
        return error_response(exception.status_code, exception.code, exception.message, request)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, _exception: Exception) -> JSONResponse:
        logger.exception(
            "Unhandled request error",
            extra={"request_id": getattr(request.state, "request_id", "unknown")},
        )
        return error_response(500, "internal_error", "An internal error occurred.", request)
