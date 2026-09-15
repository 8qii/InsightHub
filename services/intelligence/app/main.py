from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agents.analyst.agent import AnalystAgent
from app.agents.core.llm import OpenAICompatibleClient
from app.api.agent import router as agent_router
from app.api.data import router as data_router
from app.api.evaluation import router as evaluation_router
from app.api.health import router as health_router
from app.api.investigations import router as investigations_router
from app.api.knowledge import router as knowledge_router
from app.api.overview import router as overview_router
from app.config import get_settings
from app.data.database import Database
from app.errors import register_exception_handlers
from app.logging import configure_logging
from app.middleware import request_id_logging_middleware
from app.observability.runs import default_run_store
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
    llm_client = OpenAICompatibleClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )
    database = Database(settings) if settings.postgres_configured else None
    knowledge_service = KnowledgeService(client)
    application.state.knowledge_service = knowledge_service
    application.state.database = database
    application.state.run_store = default_run_store
    application.state.analyst_agent = AnalystAgent(
        llm=llm_client,
        knowledge_service=knowledge_service,
        workspace_id=settings.anythingllm_workspace_id,
        session_factory=database.session_factory if database is not None else None,
        tool_timeout_seconds=settings.agent_tool_timeout_seconds,
        max_iterations=settings.agent_max_iterations,
        max_tool_failures=settings.agent_max_tool_failures,
        timeout_seconds=settings.agent_timeout_seconds,
    )
    try:
        yield
    finally:
        await llm_client.close()
        await client.close()
        if database is not None:
            await database.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.middleware("http")(request_id_logging_middleware)
app.include_router(health_router)
app.include_router(knowledge_router)
app.include_router(data_router)
app.include_router(overview_router)
app.include_router(investigations_router)
app.include_router(agent_router)
app.include_router(evaluation_router)
register_exception_handlers(app)
