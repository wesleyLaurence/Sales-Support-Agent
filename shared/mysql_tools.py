from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import mysql.connector
from mysql.connector import MySQLConnection


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]


def _get_connection() -> MySQLConnection:
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "driftdesk_support"),
        autocommit=True,
    )


def _get_or_create_customer(cursor, email: str, full_name: str) -> int:
    cursor.execute("SELECT customer_id FROM customers WHERE email = %s", (email,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "INSERT INTO customers (email, full_name) VALUES (%s, %s)",
        (email, full_name),
    )
    return cursor.lastrowid


def create_support_ticket(
    email: str,
    full_name: str,
    subject: str,
    issue: str,
    order_id: Optional[str] = None,
    priority: str = "normal",
    channel: str = "chat",
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a support ticket and initial update entry."""
    ticket_id = f"TCK-{uuid.uuid4().hex[:6].upper()}"
    tags = tags or []

    with _get_connection() as connection:
        cursor = connection.cursor()
        customer_id = _get_or_create_customer(cursor, email, full_name)
        cursor.execute(
            """
            INSERT INTO support_tickets
              (ticket_id, customer_id, order_id, subject, status, priority, channel)
            VALUES
              (%s, %s, %s, %s, %s, %s, %s)
            """,
            (ticket_id, customer_id, order_id, subject, "open", priority, channel),
        )
        cursor.execute(
            """
            INSERT INTO ticket_updates (ticket_id, update_type, note)
            VALUES (%s, %s, %s)
            """,
            (ticket_id, "customer", issue),
        )
        for tag in tags:
            cursor.execute(
                "INSERT INTO ticket_tags (ticket_id, tag) VALUES (%s, %s)",
                (ticket_id, tag),
            )

    return {"ticket_id": ticket_id, "status": "open"}


def add_ticket_update(ticket_id: str, update_type: str, note: str) -> Dict[str, Any]:
    """Append an update to a support ticket."""
    with _get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT ticket_id FROM support_tickets WHERE ticket_id = %s", (ticket_id,)
        )
        if cursor.fetchone() is None:
            return {"error": f"Ticket not found: {ticket_id}"}
        cursor.execute(
            "INSERT INTO ticket_updates (ticket_id, update_type, note) VALUES (%s, %s, %s)",
            (ticket_id, update_type, note),
        )
    return {"ticket_id": ticket_id, "status": "updated"}


def get_ticket(ticket_id: str) -> Dict[str, Any]:
    """Fetch a ticket with latest updates."""
    with _get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM support_tickets WHERE ticket_id = %s", (ticket_id,))
        ticket = cursor.fetchone()
        if not ticket:
            return {"error": f"Ticket not found: {ticket_id}"}
        cursor.execute(
            """
            SELECT update_type, note, updated_at
            FROM ticket_updates
            WHERE ticket_id = %s
            ORDER BY updated_at DESC
            LIMIT 5
            """,
            (ticket_id,),
        )
        updates = cursor.fetchall()
        cursor.execute("SELECT tag FROM ticket_tags WHERE ticket_id = %s", (ticket_id,))
        tags = [row["tag"] for row in cursor.fetchall()]

    return {"ticket": ticket, "recent_updates": updates, "tags": tags}


def list_open_tickets(limit: int = 10) -> Dict[str, Any]:
    """List open or pending tickets."""
    with _get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT ticket_id, subject, status, priority, created_at
            FROM support_tickets
            WHERE status IN ('open', 'pending')
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (max(limit, 1),),
        )
        tickets = cursor.fetchall()
    return {"tickets": tickets, "count": len(tickets)}


def close_ticket(ticket_id: str, resolution_note: str) -> Dict[str, Any]:
    """Close a ticket and write a resolution update."""
    with _get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE support_tickets SET status = %s, closed_at = NOW() WHERE ticket_id = %s",
            ("closed", ticket_id),
        )
        if cursor.rowcount == 0:
            return {"error": f"Ticket not found: {ticket_id}"}
        cursor.execute(
            "INSERT INTO ticket_updates (ticket_id, update_type, note) VALUES (%s, %s, %s)",
            (ticket_id, "resolution", resolution_note),
        )
    return {"ticket_id": ticket_id, "status": "closed"}


TOOL_SPECS: List[ToolSpec] = [
    ToolSpec(
        name="create_support_ticket",
        description="Create a support ticket in MySQL.",
        parameters={
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "full_name": {"type": "string"},
                "subject": {"type": "string"},
                "issue": {"type": "string"},
                "order_id": {"type": "string"},
                "priority": {"type": "string", "default": "normal"},
                "channel": {"type": "string", "default": "chat"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["email", "full_name", "subject", "issue"],
        },
    ),
    ToolSpec(
        name="add_ticket_update",
        description="Append an update to a support ticket.",
        parameters={
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
                "update_type": {"type": "string"},
                "note": {"type": "string"},
            },
            "required": ["ticket_id", "update_type", "note"],
        },
    ),
    ToolSpec(
        name="get_ticket",
        description="Fetch a support ticket with recent updates.",
        parameters={
            "type": "object",
            "properties": {"ticket_id": {"type": "string"}},
            "required": ["ticket_id"],
        },
    ),
    ToolSpec(
        name="list_open_tickets",
        description="List open or pending support tickets.",
        parameters={
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 10}},
        },
    ),
    ToolSpec(
        name="close_ticket",
        description="Close a support ticket.",
        parameters={
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
                "resolution_note": {"type": "string"},
            },
            "required": ["ticket_id", "resolution_note"],
        },
    ),
]
