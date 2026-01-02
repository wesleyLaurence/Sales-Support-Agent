from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

DATA = {
    "customers": [
        {"email": "morgan@east.ai", "full_name": "Morgan Lee"},
        {"email": "riley@pluto.dev", "full_name": "Riley Chen"},
    ],
    "orders": [
        {
            "order_id": "ORD-3001",
            "customer_email": "morgan@east.ai",
            "status": "processing",
            "order_total": 449.00,
            "ordered_at": "2024-12-27",
        },
        {
            "order_id": "ORD-3002",
            "customer_email": "riley@pluto.dev",
            "status": "shipped",
            "order_total": 129.00,
            "ordered_at": "2024-12-26",
        },
    ],
    "tickets": [
        {
            "ticket_id": "TCK-DP11",
            "customer_email": "morgan@east.ai",
            "subject": "Desk assembly questions",
            "issue": "Need guidance on cable routing.",
            "priority": "normal",
            "channel": "chat",
            "tags": ["setup"],
        },
        {
            "ticket_id": "TCK-DP12",
            "customer_email": "riley@pluto.dev",
            "subject": "Lamp flickers intermittently",
            "issue": "The light flickers after 10 minutes.",
            "priority": "high",
            "channel": "email",
            "tags": ["hardware"],
        },
    ],
}


class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health"):
            payload = {"status": "ok"}
        elif self.path == "/customers":
            payload = {"customers": DATA["customers"]}
        elif self.path == "/orders":
            payload = {"orders": DATA["orders"]}
        elif self.path == "/tickets":
            payload = {"tickets": DATA["tickets"]}
        else:
            self.send_response(404)
            self.end_headers()
            return

        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def main() -> None:
    server = HTTPServer(("127.0.0.1", 8000), DummyHandler)
    print("Dummy API running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
