from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from typing import Any, Dict, List

import markdown
from email.mime.text import MIMEText


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]


def escalate_support_email(
    customer_email: str,
    subject: str,
    body: str,
    priority: str = "normal",
) -> Dict[str, Any]:
    """Escalate an issue to support staff via SMTP."""
    address = os.getenv("SUPPORT_EMAIL_ADDRESS")
    password = os.getenv("SUPPORT_EMAIL_PASSWORD")
    recipients = os.getenv("SUPPORT_ESCALATION_TO", customer_email)

    if not address or not password:
        return {"error": "Missing SUPPORT_EMAIL_ADDRESS or SUPPORT_EMAIL_PASSWORD"}

    message = body
    if any(char in message for char in ["#", "*", "_", "`", "["]):
        message = markdown.markdown(message)

    msg = MIMEText(message, "html")
    msg["Subject"] = f"[{priority.upper()}] {subject}"
    msg["From"] = f"DriftDesk Support <{address}>"
    msg["To"] = recipients

    try:
        server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server_ssl.ehlo()
        server_ssl.login(address, password)
        server_ssl.sendmail(address, recipients.split(", "), msg.as_string())
        server_ssl.close()
    except Exception as exc:
        return {"error": str(exc)}

    return {"status": "sent", "to": recipients, "priority": priority}


TOOL_SPECS: List[ToolSpec] = [
    ToolSpec(
        name="escalate_support_email",
        description="Send an escalation email to support staff.",
        parameters={
            "type": "object",
            "properties": {
                "customer_email": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "priority": {"type": "string", "default": "normal"},
            },
            "required": ["customer_email", "subject", "body"],
        },
    )
]
