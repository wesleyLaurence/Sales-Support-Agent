from __future__ import annotations

import sys

from langchain.schema import AIMessage, HumanMessage

from .agent import build_sales_agent, build_support_agent, route_message


def main() -> int:
    sales_agent = build_sales_agent()
    support_agent = build_support_agent()
    chat_histories = {"sales": [], "support": []}

    print("LangChain multi-agent ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue
        route = route_message(user_input)
        agent = sales_agent if route == "sales" else support_agent
        history = chat_histories[route]
        result = agent.invoke({"input": user_input, "chat_history": history})
        response = result.get("output", "")
        print(f"Assistant ({route}): {response}")
        history.append(HumanMessage(content=user_input))
        history.append(AIMessage(content=response))

    return 0


if __name__ == "__main__":
    sys.exit(main())
