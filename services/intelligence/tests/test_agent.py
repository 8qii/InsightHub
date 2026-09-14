import asyncio
import json
from decimal import Decimal
from typing import Any

import httpx
from fastapi.testclient import TestClient

from app.agents.analyst.agent import AnalystAgent
from app.agents.core.executor import ToolExecutor
from app.agents.core.llm import OpenAICompatibleClient
from app.agents.core.loop import AgentLoop
from app.agents.core.models import AgentResult, LLMResponse, ToolContext, ToolDefinition
from app.agents.core.registry import ToolRegistry
from app.agents.tools.definitions import (
    DiscountToolInput,
    InventoryToolInput,
    KnowledgeToolInput,
    SalesToolInput,
    build_tool_definitions,
)
from app.main import app
from app.tools.discount.models import DiscountViolations
from app.tools.inventory.models import InventoryRisk
from app.tools.knowledge.models import KnowledgeQueryResult, KnowledgeSource
from app.tools.sales.models import SalesSummary


class FakeLLM:
    def __init__(self, responses: list[LLMResponse]) -> None:
        self.responses = responses
        self.requests: list[list[dict[str, Any]]] = []

    async def complete(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> LLMResponse:
        self.requests.append(messages)
        return self.responses.pop(0)


class FakeKnowledgeService:
    async def query(self, workspace_id: str, query: str, request_id: str) -> KnowledgeQueryResult:
        assert workspace_id == "nova-retail"
        return KnowledgeQueryResult(
            answer="VIP customers may receive up to 12%.",
            sources=[KnowledgeSource(source_id="policy", title="discount_policy.md")],
            latency_ms=1,
            request_id=request_id,
        )


def llm_response(
    content: str | None = None, calls: list[tuple[str, dict[str, Any]]] | None = None
) -> LLMResponse:
    tool_calls = []
    message: dict[str, Any] = {"role": "assistant", "content": content}
    if calls:
        raw_calls = []
        for index, (name, arguments) in enumerate(calls):
            call_id = f"call-{index}"
            raw_calls.append(
                {
                    "id": call_id,
                    "type": "function",
                    "function": {"name": name, "arguments": json.dumps(arguments)},
                }
            )
            from app.agents.core.models import LLMToolCall

            tool_calls.append(LLMToolCall(call_id, name, json.dumps(arguments)))
        message["tool_calls"] = raw_calls
    return LLMResponse(message=message, content=content, tool_calls=tool_calls)


def test_agent_uses_knowledge_tool_and_returns_sources() -> None:
    llm = FakeLLM(
        [
            llm_response(calls=[("search_company_knowledge", {"query": "VIP discount"})]),
            llm_response("The maximum VIP discount allowed is 12%.")
        ]
    )
    agent = AnalystAgent(llm, FakeKnowledgeService(), "nova-retail", None, 1, 4)  # type: ignore[arg-type]

    result = asyncio.run(agent.query("What is the maximum VIP discount allowed?", "request-1"))

    assert result.answer.endswith("12%.")
    assert result.selected_tools == ["search_company_knowledge"]
    assert result.sources[0]["title"] == "discount_policy.md"


def test_tool_executor_returns_safe_failure_for_invalid_arguments() -> None:
    registry = ToolRegistry(
        build_tool_definitions(FakeKnowledgeService(), "nova-retail", None)  # type: ignore[arg-type]
    )
    result = asyncio.run(
        ToolExecutor(registry, 1).execute(
            "get_sales_summary", '{"product_name":"Luna","quarter":"bad"}', ToolContext("request")
        )
    )

    assert result.ok is False
    assert result.error == "Invalid tool arguments."


def test_agent_continues_after_tool_failure() -> None:
    llm = FakeLLM(
        [
            llm_response(calls=[("get_inventory_risk", {"age_threshold_days": 90})]),
            llm_response("Inventory data was unavailable; I cannot verify the inventory cause.")
        ]
    )
    agent = AnalystAgent(llm, FakeKnowledgeService(), "nova-retail", None, 1, 4)  # type: ignore[arg-type]

    result = asyncio.run(agent.query("Why did Luna decline?", "request-2"))

    assert "unavailable" in result.answer
    assert result.selected_tools == ["get_inventory_risk"]


def test_discount_scenario_uses_discount_tool() -> None:
    async def discount_tool(_: Any, __: ToolContext) -> DiscountViolations:
        return DiscountViolations(total_violations=180, unapproved_violations=120)

    registry = ToolRegistry(
        [
            ToolDefinition(
                name="get_discount_violations",
                description="Count discount violations.",
                input_schema=DiscountToolInput,
                execute=discount_tool,
            )
        ]
    )
    loop = AgentLoop(
        FakeLLM(
            [
                llm_response(calls=[("get_discount_violations", {"maximum_discount": 12})]),
                llm_response("There were 180 violations.")
            ]
        ),
        registry,
        1,
        3,
    )

    result = asyncio.run(loop.run("How many discount violations?", "discount-test", "Analyst"))

    assert result.selected_tools == ["get_discount_violations"]
    assert "180" in result.answer


def test_luna_scenario_uses_knowledge_sales_and_inventory() -> None:
    async def knowledge_tool(_: Any, __: ToolContext) -> dict[str, Any]:
        return {"answer": "Demand and lead times affected Luna.", "sources": []}

    async def sales_tool(arguments: Any, __: ToolContext) -> SalesSummary:
        revenue = "300000" if arguments.quarter == "Q2" else "246000"
        orders = 3000 if arguments.quarter == "Q2" else 2460
        return SalesSummary(
            product="Product Luna",
            quarter=arguments.quarter,
            revenue=Decimal(revenue),
            order_count=orders,
        )

    async def inventory_tool(_: Any, __: ToolContext) -> list[InventoryRisk]:
        return [InventoryRisk(product="Product Luna", stock_quantity=12000, age_days=138)]

    registry = ToolRegistry(
        [
            ToolDefinition(
                "search_company_knowledge", "Search documents.", KnowledgeToolInput, knowledge_tool
            ),
            ToolDefinition("get_sales_summary", "Get sales.", SalesToolInput, sales_tool),
            ToolDefinition(
                "get_inventory_risk", "Get inventory.", InventoryToolInput, inventory_tool
            ),
        ]
    )
    loop = AgentLoop(
        FakeLLM(
            [
                llm_response(
                    calls=[
                        ("search_company_knowledge", {"query": "Luna decline"}),
                        ("get_sales_summary", {"product_name": "Product Luna", "quarter": "Q2"}),
                        ("get_sales_summary", {"product_name": "Product Luna", "quarter": "Q3"}),
                        ("get_inventory_risk", {"age_threshold_days": 90}),
                    ]
                ),
                llm_response("Revenue declined 18% from 300000 to 246000; inventory risk exists.")
            ]
        ),
        registry,
        1,
        3,
    )

    result = asyncio.run(loop.run("Why did Product Luna decline?", "luna-test", "Analyst"))

    assert result.selected_tools == [
        "search_company_knowledge",
        "get_sales_summary",
        "get_sales_summary",
        "get_inventory_risk",
    ]
    assert "246000" in result.answer


def test_agent_endpoint_returns_contract() -> None:
    class FakeAgent:
        async def query(self, question: str, request_id: str) -> Any:
            assert question == "How many violations?"
            return AgentResult(
                answer="180 violations.", sources=[], selected_tools=[], iterations=1
            )

    app.state.analyst_agent = FakeAgent()
    response = TestClient(app).post(
        "/api/v1/agent/query",
        headers={"X-Request-ID": "agent-test"},
        json={"question": "How many violations?"},
    )

    assert response.status_code == 200
    assert response.json() == {"answer": "180 violations.", "sources": []}


def test_openai_compatible_client_parses_tool_calls() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call-1",
                                    "function": {"name": "get_sales_summary", "arguments": "{}"},
                                }
                            ],
                        }
                    }
                ]
            },
        )

    client = OpenAICompatibleClient(
        "http://llm.test/v1", "test-key", "gpt-5.6-luna", 1, httpx.MockTransport(handler)
    )
    try:
        result = asyncio.run(client.complete([], []))
    finally:
        asyncio.run(client.close())

    assert result.tool_calls[0].name == "get_sales_summary"
