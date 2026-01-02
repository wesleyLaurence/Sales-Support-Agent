# Sales + Support Agent (LangChain vs OpenAI Agents SDK)

This portfolio project implements the **same multi-agent sales + support assistant twice**:
- **LangChain** (`langchain_app/`)
- **OpenAI Agents SDK** (`agents_sdk/`)

Both versions share the same prompts and tool contracts so you can compare **architecture, ergonomics, and tool-calling flows** apples-to-apples.

## What This Is
DriftDesk is a fictional ergonomic office brand. The system includes:
- A **router agent** that classifies each incoming message as **sales** or **support**
- A **sales agent** focused on product discovery, pricing, and scheduling demos
- A **support agent** focused on troubleshooting, order status, and ticket workflows

It also includes optional integrations:
- **Qdrant** for vector search over product context (seeded from local fixtures)
- **MySQL** for real ticket persistence (create/update/list/close) + analytics
- **MCP Gmail Calendar adapter** for checking availability + creating calendar events
- **MCP HubSpot CRM adapter** for capturing prospect emails
- **SMTP escalation** for sending support escalation emails

## How It Works (High Level)
- The **router** returns exactly one word: `sales` or `support` (mixed requests route to `support`).
- The **sales agent**:
  - retrieves product context via Qdrant (`search_product_vectors`)
  - quotes pricing via fixtures (`get_pricing`)
  - can schedule demos via MCP calendar tools (`check_calendar_availability`, `schedule_calendar_event`)
  - can capture prospect emails via MCP HubSpot (`create_crm_contact`)
- The **support agent**:
  - retrieves product context via Qdrant (`search_product_vectors`)
  - checks order status via fixtures (`check_order_status`)
  - reads/writes **support tickets in MySQL** (`create_support_ticket`, `add_ticket_update`, etc.)
  - escalates unresolved issues via SMTP (`escalate_support_email`)

## Features
- **Two parallel implementations** (LangChain + Agents SDK) with aligned prompts and tool surfaces.
- **Deterministic demo data**:
  - pricing + orders come from JSON fixtures in `shared/data/`
  - Qdrant search uses a **deterministic hash-based embedding** (no external embedding service required)
- **MySQL ticket persistence** for structured support workflows.
- **Dummy API + ETL script** to ingest customer/order/ticket records into MySQL for analytics.
- **KPI dashboard notebook** (`notebooks/support_kpi_dashboard.ipynb`) with example charts/queries.

## Quickstart (Minimal)
Install Python deps (see `Requirements` below), set your OpenAI key, then run either implementation:

```bash
export OPENAI_API_KEY=...
python -m langchain_app.runner
```

Or:

```bash
export OPENAI_API_KEY=...
python -m agents_sdk.runner
```

## Requirements
- **Python**: 3.10+
- **Optional services** (only needed if you want those capabilities):
  - **Qdrant** (vector search)
  - **MySQL 8+** (ticket tools, ETL, KPI notebook)
  - **MCP Calendar adapter** (calendar read/write via HTTP)
  - **MCP HubSpot adapter** (lead capture via HTTP)
  - **SMTP creds** (support escalation email)

## Install Dependencies
This repo does not currently pin dependencies; here’s a workable baseline:

```bash
pip install langchain langchain-openai openai-agents mysql-connector-python pandas matplotlib jupyter qdrant-client markdown
```

## Running the Multi-Agent Demos
- **LangChain**:

```bash
python -m langchain_app.runner
```

- **OpenAI Agents SDK**:

```bash
python -m agents_sdk.runner
```

## Qdrant (Vector Search)
The sales/support agents can retrieve product context from Qdrant via `search_product_vectors`.

1) Start a local Qdrant instance (defaults assume `http://localhost:6333`).
2) Seed the collection with products from `shared/data/products.json`:

```bash
python scripts/qdrant_seed.py
```

Environment variables:

```bash
export QDRANT_URL=http://localhost:6333
export QDRANT_COLLECTION=driftdesk_products
export QDRANT_VECTOR_DIM=128
```

## MySQL (Ticket Persistence + Analytics)
The support agent writes tickets to MySQL via `shared/mysql_tools.py`.

1) Create schema + seed sample data:

```bash
mysql -u root -p < sql/schema.sql
mysql -u root -p < sql/seed.sql
```

2) Configure connection:

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=...
export MYSQL_DATABASE=driftdesk_support
```

## MCP Gmail Calendar (Sales Scheduling)
The sales agent can check availability and create calendar events via an MCP-style HTTP adapter.

Set:

```bash
export MCP_GCAL_BASE_URL=http://localhost:3000
```

Expected JSON `POST` endpoints:
- `/calendar/availability` with `calendar_id`, `start`, `end`, `timezone`
- `/calendar/events` with `calendar_id`, `title`, `start`, `end`, `timezone`, `attendees`, `description`, `location`

## MCP HubSpot CRM (Lead Capture)
The sales agent can capture prospect emails and create CRM contacts via a HubSpot MCP adapter.

Set:

```bash
export MCP_HUBSPOT_BASE_URL=http://localhost:3001
```

Expected JSON `POST` endpoint:
- `/crm/contacts` with `email`, `first_name`, `last_name`, `company`, `phone`, `source`

## Support Escalation Email (SMTP)
Support escalation uses Gmail SMTP via `shared/support_tools.py`.

```bash
export SUPPORT_EMAIL_ADDRESS=...
export SUPPORT_EMAIL_PASSWORD=...
export SUPPORT_ESCALATION_TO=ops@example.com
```

## Dummy API + ETL
For testing and analytics, there’s a tiny dummy HTTP API plus an ETL script that loads its data into MySQL.

Run the dummy API:

```bash
python scripts/dummy_api.py
```

Run the ETL:

```bash
python scripts/etl_sync.py
```

Override the API base URL if needed:

```bash
export DUMMY_API_URL=http://127.0.0.1:8000
```

## KPI Notebook
The notebook connects to MySQL and renders basic KPI summaries and charts:

```bash
jupyter notebook notebooks/support_kpi_dashboard.ipynb
```

## Project Layout
- `shared/`: shared prompts, fixtures, and tool implementations
  - `shared/data/`: product/pricing/order fixtures
  - `shared/prompts/`: router + sales + support instructions
  - `shared/qdrant_tools.py`: Qdrant search + deterministic embedding + seeding helper
  - `shared/mysql_tools.py`: MySQL ticket CRUD tools
  - `shared/mcp_calendar_tools.py`: MCP calendar HTTP client tools
  - `shared/mcp_hubspot_tools.py`: MCP HubSpot CRM HTTP client tools
  - `shared/support_tools.py`: SMTP escalation tool
- `langchain_app/`: LangChain multi-agent implementation (router → sales/support)
- `agents_sdk/`: OpenAI Agents SDK multi-agent implementation (router → sales/support)
- `sql/`: schema + seed scripts for MySQL
- `scripts/`: Qdrant seeding, dummy API, ETL, eval replay
- `notebooks/`: support KPI dashboard

## Scripts
- `scripts/qdrant_seed.py`: seeds Qdrant with product vectors
- `scripts/dummy_api.py`: serves dummy customers/orders/tickets for ETL
- `scripts/etl_sync.py`: loads dummy API data into MySQL (customers, orders, tickets)
- `scripts/eval_replay.py`: replays sample queries through both implementations

## Notes / Design Intent
- **Prompts and tool signatures are intentionally aligned** across LangChain and Agents SDK versions.
- **External services are optional**; you can run the agents without Qdrant/MySQL/MCP/SMTP, but tool calls will error until configured.
- Agent outputs and routing are **model-driven**; set temperature to `0` if you want more repeatable behavior.
