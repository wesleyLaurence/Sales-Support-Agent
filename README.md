# Sales + Support Agent (LangChain vs Agents SDK)

This portfolio project builds the *same* sales/support agent twice: once with LangChain, once with the OpenAI Agents SDK. The goal is to compare ergonomics, structure, and tool-calling flows while keeping behavior and tool contracts identical.

## Overview
- Multi-agent system with a router, sales agent, and support agent
- Two implementations with aligned prompts and tool surfaces for comparison
- Qdrant vector search for product context + MySQL ticket persistence

## How It Works
- A router agent classifies each user request as sales or support.
- Sales agent uses Qdrant for product context and pricing tools.
- Support agent uses Qdrant, MySQL ticket tools, and escalation email via SMTP.
- Data is sourced from local JSON fixtures, Qdrant vectors, and MySQL tables.
- A dummy API + ETL pipeline loads additional ticket data into MySQL for analytics.

## Features
- Router agent for sales vs support intent.
- Sales tools:
  - `search_product_vectors` (Qdrant vector search)
  - `get_pricing` (SKU -> price, promo rules)
  - `check_calendar_availability` (Gmail Calendar via MCP)
  - `schedule_calendar_event` (Gmail Calendar via MCP)
- Support tools:
  - `search_product_vectors` (Qdrant vector search)
  - `check_order_status` (order id -> status)
  - MySQL ticket tools (create, update, list, close)
  - `escalate_support_email` (SMTP escalation)
- Deterministic tool outputs via local JSON fixtures and hash-based embeddings.
- MySQL-backed support ticket tools for read/write operations.
- Dummy API + ETL pipeline to ingest data into MySQL.
- KPI dashboard notebook for support analytics.
- Minimal CLI runner for local demo.
- Consistent example conversations.

## Architecture
- Shared layer in `shared/` defines prompts, fixtures, and tool logic.
- Router agent chooses between sales and support sub-agents.
- Sales agent: Qdrant product retrieval + pricing.
- Support agent: Qdrant retrieval + MySQL tickets + escalation email.
- Optional MySQL path adds real persistence for ticket workflows.
- ETL loads dummy API data into MySQL to fuel analytics.

## Project Layout
- `shared/`
  - `data/` fixture JSON for products, pricing, orders
  - `prompts/` shared system prompt + examples
  - `tools.py` shared tool interfaces + logic
  - `mysql_tools.py` MySQL-backed ticket tools
  - `qdrant_tools.py` Qdrant search utilities
  - `support_tools.py` escalation utilities
  - `mcp_calendar_tools.py` MCP Gmail Calendar tools
- `langchain_app/` LangChain implementation
- `agents_sdk/` OpenAI Agents SDK implementation
- `sql/` MySQL schema + seed data
- `notebooks/` KPI dashboard notebook
- `scripts/` run demos and evals

## Requirements
- Python 3.10+
- Optional: MySQL 8+ (for ticket tools, ETL, and KPIs)
- Optional: Qdrant (for vector search)

## Setup
Install dependencies:
```
pip install langchain langchain-openai openai-agents mysql-connector-python pandas matplotlib jupyter qdrant-client markdown
```

Set your API key:
```
export OPENAI_API_KEY=...
```

## Run the Agents
LangChain:
```
python -m langchain_app.runner
```

Agents SDK:
```
python -m agents_sdk.runner
```

## Qdrant Setup
Start a local Qdrant instance, then seed product vectors:
```
python scripts/qdrant_seed.py
```
Configure via environment variables if needed:
```
export QDRANT_URL=http://localhost:6333
export QDRANT_COLLECTION=driftdesk_products
export QDRANT_VECTOR_DIM=128
```

## MCP Gmail Calendar
The sales agent can check availability and schedule events via a Gmail Calendar MCP service.
Set the MCP base URL to your MCP calendar adapter:
```
export MCP_GCAL_BASE_URL=http://localhost:3000
```
Expected endpoints (JSON POST):
- `/calendar/availability` with `calendar_id`, `start`, `end`, `timezone`
- `/calendar/events` with `calendar_id`, `title`, `start`, `end`, `timezone`, `attendees`, `description`, `location`

## MySQL Schema + Seed
```
mysql -u root -p < sql/schema.sql
mysql -u root -p < sql/seed.sql
```

## MySQL Tools
The MySQL-backed tools live in `shared/mysql_tools.py` and handle ticket creation, updates, and queries.
Set these environment variables before running:
```
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=...
export MYSQL_DATABASE=driftdesk_support
```

## Escalation Email (SMTP)
Support escalation uses Gmail SMTP. Configure:
```
export SUPPORT_EMAIL_ADDRESS=...
export SUPPORT_EMAIL_PASSWORD=...
export SUPPORT_ESCALATION_TO=ops@example.com
```

## Dummy API + ETL
Start the local dummy API, then run the ETL to load data into MySQL:
```
python scripts/dummy_api.py
python scripts/etl_sync.py
```
You can override the API base URL with:
```
export DUMMY_API_URL=http://127.0.0.1:8000
```

## KPI Notebook
Open the KPI dashboard:
```
jupyter notebook notebooks/support_kpi_dashboard.ipynb
```

## Scripts
- `scripts/eval_replay.py` replays sample queries through both agents.
- `scripts/dummy_api.py` serves dummy JSON data for ETL.
- `scripts/etl_sync.py` loads dummy API data into MySQL.
- `scripts/qdrant_seed.py` seeds Qdrant with product vectors.

## Notes
- Implementation should keep tool signatures aligned across versions.
- Local fixtures drive pricing/order status; Qdrant, MySQL, MCP, and SMTP are optional external services.
- LLM routing/agent replies are nondeterministic unless you set model temperature to 0.
