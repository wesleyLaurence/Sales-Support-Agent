from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict
from urllib.request import urlopen

import mysql.connector

DEFAULT_API = "http://127.0.0.1:8000"


def _get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "driftdesk_support"),
        autocommit=True,
    )


def _fetch_json(url: str) -> Dict[str, Any]:
    with urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_or_create_customer(cursor, email: str, full_name: str) -> int:
    cursor.execute("SELECT customer_id FROM customers WHERE email = %s", (email,))
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE customers SET full_name = %s WHERE customer_id = %s",
            (full_name, row[0]),
        )
        return row[0]
    cursor.execute(
        "INSERT INTO customers (email, full_name) VALUES (%s, %s)",
        (email, full_name),
    )
    return cursor.lastrowid


def _ingest_customers(cursor, base_url: str) -> int:
    payload = _fetch_json(f"{base_url}/customers")
    count = 0
    for customer in payload.get("customers", []):
        _get_or_create_customer(cursor, customer["email"], customer["full_name"])
        count += 1
    return count


def _ingest_orders(cursor, base_url: str) -> int:
    payload = _fetch_json(f"{base_url}/orders")
    count = 0
    for order in payload.get("orders", []):
        customer_id = _get_or_create_customer(
            cursor, order["customer_email"], order["customer_email"].split("@")[0].title()
        )
        cursor.execute(
            """
            INSERT INTO orders (order_id, customer_id, status, order_total, ordered_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              status = VALUES(status),
              order_total = VALUES(order_total),
              ordered_at = VALUES(ordered_at)
            """,
            (
                order["order_id"],
                customer_id,
                order["status"],
                order["order_total"],
                order["ordered_at"],
            ),
        )
        count += 1
    return count


def _ingest_tickets(cursor, base_url: str) -> int:
    payload = _fetch_json(f"{base_url}/tickets")
    count = 0
    for ticket in payload.get("tickets", []):
        customer_id = _get_or_create_customer(
            cursor, ticket["customer_email"], ticket["customer_email"].split("@")[0].title()
        )
        cursor.execute(
            """
            INSERT INTO support_tickets
              (ticket_id, customer_id, subject, status, priority, channel)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              status = VALUES(status),
              priority = VALUES(priority),
              channel = VALUES(channel)
            """,
            (
                ticket["ticket_id"],
                customer_id,
                ticket["subject"],
                "open",
                ticket.get("priority", "normal"),
                ticket.get("channel", "chat"),
            ),
        )
        cursor.execute(
            """
            INSERT INTO ticket_updates (ticket_id, update_type, note)
            VALUES (%s, %s, %s)
            """,
            (ticket["ticket_id"], "customer", ticket["issue"]),
        )
        for tag in ticket.get("tags", []):
            cursor.execute(
                "INSERT IGNORE INTO ticket_tags (ticket_id, tag) VALUES (%s, %s)",
                (ticket["ticket_id"], tag),
            )
        count += 1
    return count


def run_etl(base_url: str) -> None:
    with _get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO etl_ingest_log (source, status) VALUES (%s, %s)",
            (base_url, "running"),
        )
        ingest_id = cursor.lastrowid

        total = 0
        total += _ingest_customers(cursor, base_url)
        total += _ingest_orders(cursor, base_url)
        total += _ingest_tickets(cursor, base_url)

        cursor.execute(
            """
            UPDATE etl_ingest_log
            SET records_loaded = %s, finished_at = %s, status = %s
            WHERE ingest_id = %s
            """,
            (total, datetime.utcnow(), "success", ingest_id),
        )


if __name__ == "__main__":
    api_url = os.getenv("DUMMY_API_URL", DEFAULT_API)
    run_etl(api_url)
    print(f"ETL completed from {api_url}")
