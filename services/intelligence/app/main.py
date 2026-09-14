from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.data import router as data_router
from app.api.health import router as health_router
from app.api.knowledge import router as knowledge_router
from app.config import get_settings
from app.data.database import Database
from app.errors import register_exception_handlers
from app.logging import configure_logging
from app.middleware import request_id_logging_middleware
from app.tools.knowledge.client import AnythingLLMClient
from app.tools.knowledge.service import KnowledgeService

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    client = AnythingLLMClient(
        base_url=settings.anythingllm_base_url,
        api_key=settings.anythingllm_api_key,
        timeout_seconds=settings.anythingllm_timeout_seconds,
    )
    database = Database(settings) if settings.postgres_configured else None
    application.state.knowledge_service = KnowledgeService(client)
    application.state.database = database
    try:
        yield
    finally:
        await client.close()
        if database is not None:
            await database.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.middleware("http")(request_id_logging_middleware)
app.include_router(health_router)
app.include_router(knowledge_router)
app.include_router(data_router)
register_exception_handlers(app)
