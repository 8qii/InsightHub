from fastapi import FastAPI

from app.api.health import router as health_router
from app.config import get_settings
from app.errors import register_exception_handlers
from app.logging import configure_logging
from app.middleware import request_id_logging_middleware

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
app.middleware("http")(request_id_logging_middleware)
app.include_router(health_router)
register_exception_handlers(app)
