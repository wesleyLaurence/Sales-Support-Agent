from __future__ import annotations

from pathlib import Path

from agents import Agent, Runner, function_tool

from shared import (
    mcp_calendar_tools,
    mcp_hubspot_tools,
    mysql_tools,
    qdrant_tools,
    support_tools,
    tools as shared_tools,
)

PROMPT_DIR = Path(__file__).resolve().parents[1] / "shared" / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


@function_tool
def search_product_vectors(query: str, limit: int = 3):
    return qdrant_tools.search_product_vectors(query, limit)


@function_tool
def get_pricing(sku: str, quantity: int = 1, promo_code: str | None = None):
    return shared_tools.get_pricing(sku, quantity, promo_code)


@function_tool
def check_order_status(order_id: str):
    return shared_tools.check_order_status(order_id)


@function_tool
def create_support_ticket(
    email: str,
    full_name: str,
    subject: str,
    issue: str,
    order_id: str | None = None,
    priority: str = "normal",
    channel: str = "chat",
    tags: list[str] | None = None,
):
    return mysql_tools.create_support_ticket(
        email, full_name, subject, issue, order_id, priority, channel, tags
    )


@function_tool
def add_ticket_update(ticket_id: str, update_type: str, note: str):
    return mysql_tools.add_ticket_update(ticket_id, update_type, note)


@function_tool
def get_ticket(ticket_id: str):
    return mysql_tools.get_ticket(ticket_id)


@function_tool
def list_open_tickets(limit: int = 10):
    return mysql_tools.list_open_tickets(limit)


@function_tool
def close_ticket(ticket_id: str, resolution_note: str):
    return mysql_tools.close_ticket(ticket_id, resolution_note)


@function_tool
def escalate_support_email(
    customer_email: str, subject: str, body: str, priority: str = "normal"
):
    return support_tools.escalate_support_email(customer_email, subject, body, priority)


@function_tool
def check_calendar_availability(
    calendar_id: str, start_iso: str, end_iso: str, timezone: str = "UTC"
):
    return mcp_calendar_tools.check_calendar_availability(
        calendar_id, start_iso, end_iso, timezone
    )


@function_tool
def schedule_calendar_event(
    calendar_id: str,
    title: str,
    start_iso: str,
    end_iso: str,
    attendees: list[str] | None = None,
    timezone: str = "UTC",
    description: str | None = None,
    location: str | None = None,
):
    return mcp_calendar_tools.schedule_calendar_event(
        calendar_id,
        title,
        start_iso,
        end_iso,
        attendees,
        timezone,
        description,
        location,
    )


@function_tool
def create_crm_contact(
    email: str,
    first_name: str | None = None,
    last_name: str | None = None,
    company: str | None = None,
    phone: str | None = None,
    source: str = "sales_agent",
):
    return mcp_hubspot_tools.create_crm_contact(
        email,
        first_name,
        last_name,
        company,
        phone,
        source,
    )


def build_sales_agent(model: str = "gpt-4o-mini") -> Agent:
    return Agent(
        name="DriftDesk Sales",
        instructions=_load_prompt("sales.md"),
        model=model,
        tools=[
            search_product_vectors,
            get_pricing,
            check_calendar_availability,
            schedule_calendar_event,
            create_crm_contact,
        ],
    )


def build_support_agent(model: str = "gpt-4o-mini") -> Agent:
    return Agent(
        name="DriftDesk Support",
        instructions=_load_prompt("support.md"),
        model=model,
        tools=[
            search_product_vectors,
            check_order_status,
            create_support_ticket,
            add_ticket_update,
            get_ticket,
            list_open_tickets,
            close_ticket,
            escalate_support_email,
        ],
    )


def build_router_agent(model: str = "gpt-4o-mini") -> Agent:
    return Agent(
        name="DriftDesk Router",
        instructions=_load_prompt("router.md"),
        model=model,
    )


def route_message(user_input: str, model: str = "gpt-4o-mini") -> str:
    router = build_router_agent(model)
    result = Runner.run_sync(router, user_input)
    route = result.final_output.strip().lower()
    if route not in {"sales", "support"}:
        return "support"
    return route
