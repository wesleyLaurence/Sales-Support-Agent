from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent / "data"


def _load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


_PRODUCTS = _load_json("products.json")
_PRICING = _load_json("pricing.json")
_ORDERS = _load_json("orders.json")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]


def search_products(keywords: str, category: Optional[str] = None, limit: int = 3) -> Dict[str, Any]:
    """Search products by keywords and optional category."""
    tokens = [token.strip().lower() for token in keywords.split() if token.strip()]
    matches: List[Dict[str, Any]] = []

    for product in _PRODUCTS:
        if category and product["category"].lower() != category.lower():
            continue
        haystack = " ".join(
            [product["name"], product["description"], " ".join(product.get("tags", []))]
        ).lower()
        if all(token in haystack for token in tokens):
            matches.append(product)

    return {"matches": matches[: max(limit, 1)], "count": len(matches)}


def get_pricing(
    sku: str, quantity: int = 1, promo_code: Optional[str] = None
) -> Dict[str, Any]:
    """Return pricing details for a SKU."""
    items = _PRICING["items"]
    if sku not in items:
        return {"error": f"Unknown SKU: {sku}"}

    unit_price = items[sku]["unit_price"]
    qty = max(int(quantity), 1)
    subtotal = unit_price * qty
    discount = 0.0
    promo_applied = None

    promos = _PRICING.get("promos", {})
    if promo_code:
        promo = promos.get(promo_code.upper())
        if promo and subtotal >= promo.get("min_subtotal", 0):
            percent_off = promo.get("percent_off", 0)
            discount = round(subtotal * (percent_off / 100), 2)
            promo_applied = promo_code.upper()

    total = round(subtotal - discount, 2)
    return {
        "sku": sku,
        "quantity": qty,
        "unit_price": unit_price,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
        "currency": _PRICING.get("currency", "USD"),
        "promo": promo_applied,
    }


def check_order_status(order_id: str) -> Dict[str, Any]:
    """Return order status details."""
    order = _ORDERS.get(order_id)
    if not order:
        return {"error": f"Order not found: {order_id}"}
    return {"order_id": order_id, **order}


def open_support_ticket(
    issue: str,
    email: str,
    order_id: Optional[str] = None,
    priority: str = "normal",
) -> Dict[str, Any]:
    """Open a deterministic support ticket."""
    payload = f"{issue}|{email}|{order_id or ''}|{priority}"
    ticket_id = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:8].upper()
    return {
        "ticket_id": f"TCK-{ticket_id}",
        "status": "open",
        "priority": priority,
        "order_id": order_id,
    }


TOOL_SPECS: List[ToolSpec] = [
    ToolSpec(
        name="search_products",
        description="Search the product catalog by keywords and optional category.",
        parameters={
            "type": "object",
            "properties": {
                "keywords": {"type": "string"},
                "category": {"type": "string"},
                "limit": {"type": "integer", "default": 3},
            },
            "required": ["keywords"],
        },
    ),
    ToolSpec(
        name="get_pricing",
        description="Get pricing for a SKU with quantity and optional promo code.",
        parameters={
            "type": "object",
            "properties": {
                "sku": {"type": "string"},
                "quantity": {"type": "integer", "default": 1},
                "promo_code": {"type": "string"},
            },
            "required": ["sku"],
        },
    ),
    ToolSpec(
        name="check_order_status",
        description="Check the status of an order.",
        parameters={
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    ),
    ToolSpec(
        name="open_support_ticket",
        description="Open a support ticket for a customer issue.",
        parameters={
            "type": "object",
            "properties": {
                "issue": {"type": "string"},
                "email": {"type": "string"},
                "order_id": {"type": "string"},
                "priority": {"type": "string", "default": "normal"},
            },
            "required": ["issue", "email"],
        },
    ),
]


def tool_spec_map() -> Dict[str, Dict[str, Any]]:
    return {
        spec.name: {"description": spec.description, "parameters": spec.parameters}
        for spec in TOOL_SPECS
    }
