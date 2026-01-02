from __future__ import annotations

import sys

from agents import Runner

from .multi_agent import build_sales_agent, build_support_agent, route_message


def main() -> int:
    sales_agent = build_sales_agent()
    support_agent = build_support_agent()

    print("Agents SDK multi-agent ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue
        route = route_message(user_input)
        agent = sales_agent if route == "sales" else support_agent
        result = Runner.run_sync(agent, user_input)
        print(f"Assistant ({route}): {result.final_output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
