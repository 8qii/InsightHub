from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.errors import AppError, register_exception_handlers
from app.middleware import request_id_logging_middleware


def create_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.middleware("http")(request_id_logging_middleware)
    register_exception_handlers(test_app)

    @test_app.get("/known-error")
    async def known_error() -> None:
        raise AppError(400, "known_error", "A known error occurred.")

    @test_app.get("/unexpected-error")
    async def unexpected_error() -> None:
        raise RuntimeError("sensitive internal detail")

    return test_app


def test_known_error_uses_safe_envelope() -> None:
    response = TestClient(create_test_app()).get("/known-error")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "known_error"
    assert response.json()["error"]["request_id"]


def test_unexpected_error_hides_internal_details() -> None:
    response = TestClient(create_test_app(), raise_server_exceptions=False).get("/unexpected-error")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "sensitive internal detail" not in response.text
