from __future__ import annotations

from pathlib import Path

from agents import Agent, function_tool

from shared import tools as shared_tools

PROMPT_PATH = Path(__file__).resolve().parents[1] / "shared" / "prompts" / "system.md"


@function_tool
def search_products(keywords: str, category: str | None = None, limit: int = 3):
    return shared_tools.search_products(keywords, category, limit)


@function_tool
def get_pricing(sku: str, quantity: int = 1, promo_code: str | None = None):
    return shared_tools.get_pricing(sku, quantity, promo_code)


@function_tool
def check_order_status(order_id: str):
    return shared_tools.check_order_status(order_id)


@function_tool
def open_support_ticket(
    issue: str, email: str, order_id: str | None = None, priority: str = "normal"
):
    return shared_tools.open_support_ticket(issue, email, order_id, priority)


def _load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_agent(model: str = "gpt-4o-mini") -> Agent:
    return Agent(
        name="DriftDesk Assistant",
        instructions=_load_system_prompt(),
        model=model,
        tools=[
            search_products,
            get_pricing,
            check_order_status,
            open_support_ticket,
        ],
    )
