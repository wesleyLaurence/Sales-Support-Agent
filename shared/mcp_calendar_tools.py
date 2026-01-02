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
    return os.getenv("MCP_GCAL_BASE_URL", "").rstrip("/")


def _post_json(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    base = _base_url()
    if not base:
        return {"error": "Missing MCP_GCAL_BASE_URL"}

    url = f"{base}{path}"
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {"error": str(exc)}


def check_calendar_availability(
    calendar_id: str,
    start_iso: str,
    end_iso: str,
    timezone: str = "UTC",
) -> Dict[str, Any]:
    """Check calendar availability via MCP."""
    payload = {
        "calendar_id": calendar_id,
        "start": start_iso,
        "end": end_iso,
        "timezone": timezone,
    }
    return _post_json("/calendar/availability", payload)


def schedule_calendar_event(
    calendar_id: str,
    title: str,
    start_iso: str,
    end_iso: str,
    attendees: Optional[List[str]] = None,
    timezone: str = "UTC",
    description: Optional[str] = None,
    location: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a calendar event via MCP."""
    payload = {
        "calendar_id": calendar_id,
        "title": title,
        "start": start_iso,
        "end": end_iso,
        "timezone": timezone,
        "attendees": attendees or [],
        "description": description,
        "location": location,
    }
    return _post_json("/calendar/events", payload)


TOOL_SPECS: List[ToolSpec] = [
    ToolSpec(
        name="check_calendar_availability",
        description="Check calendar availability via MCP Gmail Calendar.",
        parameters={
            "type": "object",
            "properties": {
                "calendar_id": {"type": "string"},
                "start_iso": {"type": "string"},
                "end_iso": {"type": "string"},
                "timezone": {"type": "string", "default": "UTC"},
            },
            "required": ["calendar_id", "start_iso", "end_iso"],
        },
    ),
    ToolSpec(
        name="schedule_calendar_event",
        description="Create a new event on a calendar via MCP Gmail Calendar.",
        parameters={
            "type": "object",
            "properties": {
                "calendar_id": {"type": "string"},
                "title": {"type": "string"},
                "start_iso": {"type": "string"},
                "end_iso": {"type": "string"},
                "attendees": {"type": "array", "items": {"type": "string"}},
                "timezone": {"type": "string", "default": "UTC"},
                "description": {"type": "string"},
                "location": {"type": "string"},
            },
            "required": ["calendar_id", "title", "start_iso", "end_iso"],
        },
    ),
]
