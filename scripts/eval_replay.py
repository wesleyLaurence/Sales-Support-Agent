from __future__ import annotations

from typing import List

SAMPLE_QUERIES: List[str] = [
    "I'm looking for a standing desk with a bamboo top.",
    "What's the price on DSK-100 for two units with BUNDLE10?",
    "Order ORD-1002 says it's late.",
]


def _run_langchain() -> None:
    try:
        from langchain.schema import HumanMessage

        from langchain_app.agent import build_sales_agent, build_support_agent, route_message
    except ImportError as exc:
        print(f"[langchain] Skipped: {exc}")
        return

    sales_agent = build_sales_agent()
    support_agent = build_support_agent()
    chat_histories = {"sales": [], "support": []}
    print("\n[langchain] Running sample queries")
    for query in SAMPLE_QUERIES:
        route = route_message(query)
        agent = sales_agent if route == "sales" else support_agent
        history = chat_histories[route]
        result = agent.invoke({"input": query, "chat_history": history})
        print(f"User: {query}")
        print(f"Assistant ({route}): {result.get('output', '')}")
        history.append(HumanMessage(content=query))


def _run_agents_sdk() -> None:
    try:
        from agents import Runner

        from agents_sdk.multi_agent import build_sales_agent, build_support_agent, route_message
    except ImportError as exc:
        print(f"[agents-sdk] Skipped: {exc}")
        return

    sales_agent = build_sales_agent()
    support_agent = build_support_agent()
    print("\n[agents-sdk] Running sample queries")
    for query in SAMPLE_QUERIES:
        route = route_message(query)
        agent = sales_agent if route == "sales" else support_agent
        result = Runner.run_sync(agent, query)
        print(f"User: {query}")
        print(f"Assistant ({route}): {result.final_output}")


def main() -> None:
    _run_langchain()
    _run_agents_sdk()


if __name__ == "__main__":
    main()
