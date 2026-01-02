from __future__ import annotations

from pathlib import Path

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from shared import (
    mcp_calendar_tools,
    mysql_tools,
    qdrant_tools,
    support_tools,
    tools as shared_tools,
)

PROMPT_DIR = Path(__file__).resolve().parents[1] / "shared" / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def _build_prompt(system_text: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_text),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )


def build_sales_agent(model: str = "gpt-4o-mini") -> AgentExecutor:
    tools = [
        StructuredTool.from_function(qdrant_tools.search_product_vectors),
        StructuredTool.from_function(mcp_calendar_tools.check_calendar_availability),
        StructuredTool.from_function(mcp_calendar_tools.schedule_calendar_event),
        StructuredTool.from_function(shared_tools.get_pricing),
    ]
    agent = create_tool_calling_agent(
        ChatOpenAI(model=model),
        tools,
        _build_prompt(_load_prompt("sales.md")),
    )
    return AgentExecutor(agent=agent, tools=tools, verbose=False)


def build_support_agent(model: str = "gpt-4o-mini") -> AgentExecutor:
    tools = [
        StructuredTool.from_function(qdrant_tools.search_product_vectors),
        StructuredTool.from_function(shared_tools.check_order_status),
        StructuredTool.from_function(mysql_tools.create_support_ticket),
        StructuredTool.from_function(mysql_tools.add_ticket_update),
        StructuredTool.from_function(mysql_tools.get_ticket),
        StructuredTool.from_function(mysql_tools.list_open_tickets),
        StructuredTool.from_function(mysql_tools.close_ticket),
        StructuredTool.from_function(support_tools.escalate_support_email),
    ]
    agent = create_tool_calling_agent(
        ChatOpenAI(model=model),
        tools,
        _build_prompt(_load_prompt("support.md")),
    )
    return AgentExecutor(agent=agent, tools=tools, verbose=False)


def build_router(model: str = "gpt-4o-mini") -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", _load_prompt("router.md")),
            ("human", "{input}"),
        ]
    )


def route_message(user_input: str, model: str = "gpt-4o-mini") -> str:
    prompt = build_router(model)
    llm = ChatOpenAI(model=model)
    response = llm.invoke(prompt.format_messages(input=user_input))
    route = response.content.strip().lower()
    if route not in {"sales", "support"}:
        return "support"
    return route
