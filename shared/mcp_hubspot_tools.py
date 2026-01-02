from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]


def _base_url() -> str:
    return os.getenv("MCP_HUBSPOT_BASE_URL", "").rstrip("/")


def _post_json(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    base = _base_url()
    if not base:
        return {"error": "Missing MCP_HUBSPOT_BASE_URL"}

    url = f"{base}{path}"
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"error": str(exc)}


def create_crm_contact(
    email: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    company: Optional[str] = None,
    phone: Optional[str] = None,
    source: str = "sales_agent",
) -> Dict[str, Any]:
    """Create a CRM contact via HubSpot MCP."""
    payload = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "company": company,
        "phone": phone,
        "source": source,
    }
    return _post_json("/crm/contacts", payload)


TOOL_SPECS: List[ToolSpec] = [
    ToolSpec(
        name="create_crm_contact",
        description="Capture a prospect email and create a HubSpot CRM contact.",
        parameters={
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "company": {"type": "string"},
                "phone": {"type": "string"},
                "source": {"type": "string", "default": "sales_agent"},
            },
            "required": ["email"],
        },
    ),
]
