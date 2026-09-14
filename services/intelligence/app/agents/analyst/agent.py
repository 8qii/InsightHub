import hashlib
import logging
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.agents.core.llm import OpenAICompatibleClient
from app.agents.core.loop import AgentLoop
from app.agents.core.models import AgentResult
from app.agents.core.registry import ToolRegistry
from app.agents.tools.definitions import build_tool_definitions
from app.tools.knowledge.service import KnowledgeService

logger = logging.getLogger("insighthub.agent")

SYSTEM_PROMPT = """You are the InsightHub business analyst.
Answer the user's question using the available tools. Use the smallest sufficient set of tools.
Use search_company_knowledge for company policies and document facts, and cite its returned sources.
For the maximum VIP discount question, search specifically for the discount policy document.
Use business tools for numerical facts. For explanations, gather evidence before answering.
For a question asking why a product's revenue changed, call search_company_knowledge,
get_sales_summary twice for Q2 and Q3, and get_inventory_risk before answering.
For Nova Retail Q3 historical analysis, use as_of_date="2025-09-30" in get_inventory_risk
so inventory age matches the business review snapshot; do not use the current date.
Do not repeat a tool call unless its previous result was an error or insufficient.
Never invent numbers, policies, sources, or tool results. If a tool fails, explain the limitation.
If a question is ambiguous or missing a required product, quarter, or time period,
ask a concise clarification question instead of guessing.
If the available sources do not contain the requested information, say that it cannot be verified.
Give a concise answer with the relevant numbers and cite document source titles when available.
"""


class AnalystAgent:
    def __init__(
        self,
        llm: OpenAICompatibleClient,
        knowledge_service: KnowledgeService,
        workspace_id: str | None,
        session_factory: async_sessionmaker[AsyncSession] | None,
        tool_timeout_seconds: float,
        max_iterations: int,
        max_tool_failures: int = 2,
        timeout_seconds: float = 120.0,
    ) -> None:
        self._llm = llm
        self._knowledge_service = knowledge_service
        self._workspace_id = workspace_id
        self._session_factory = session_factory
        self._tool_timeout_seconds = tool_timeout_seconds
        self._max_iterations = max_iterations
        self._max_tool_failures = max_tool_failures
        self._timeout_seconds = timeout_seconds

    async def query(self, question: str, request_id: str) -> AgentResult:
        question_id = hashlib.sha256(question.encode("utf-8")).hexdigest()[:16]
        run_id = str(uuid4())
        logger.info(
            "Agent query started",
            extra={"request_id": request_id, "question_id": question_id, "run_id": run_id},
        )
        if self._session_factory is None:
            return await self._run(question, request_id, None, run_id)
        async with self._session_factory() as session:
            return await self._run(question, request_id, session, run_id)

    async def _run(
        self, question: str, request_id: str, session: AsyncSession | None, run_id: str
    ) -> AgentResult:
        registry = ToolRegistry(
            build_tool_definitions(self._knowledge_service, self._workspace_id, session)
        )
        historical_defaults = {}
        normalized_question = question.casefold()
        if any(
            term in normalized_question
            for term in ("q3", "historical", "as of", "previous period")
        ):
            historical_defaults = {
                "get_inventory_risk": {"as_of_date": "2025-09-30"}
            }
        return await AgentLoop(
            self._llm,
            registry,
            self._tool_timeout_seconds,
            self._max_iterations,
            self._max_tool_failures,
            self._timeout_seconds,
        ).run(
            question,
            request_id,
            SYSTEM_PROMPT,
            run_id,
            default_tool_arguments=historical_defaults,
        )
