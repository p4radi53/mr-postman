"""
Send the rendered HTML email via Gmail SMTP using an App Password.

Credentials are read from the validated Settings object (env / .env file):
  GMAIL_USER          – the Gmail address used to send (e.g. yourname@gmail.com)
  GMAIL_APP_PASSWORD  – the 16-character Google App Password
  RECIPIENT_EMAIL     – destination address
"""

from __future__ import annotations

import logging
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mr_postman.config import get_settings

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send(html_body: str, date: datetime | None = None) -> None:
    """Send the digest email."""
    if date is None:
        date = datetime.now(tz=timezone.utc)

    settings = get_settings()

    subject = f"Mr. Postman — Daily Digest {date.strftime('%A, %d %B %Y')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Mr. Postman <{settings.gmail_user}>"
    msg["To"] = settings.recipient_email

    # Attach plain-text fallback first, then HTML
    plain_fallback = (
        "Your email client does not support HTML. "
        "Please view this email in a client that supports HTML."
    )
    msg.attach(MIMEText(plain_fallback, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    logger.info("Connecting to %s:%d …", SMTP_HOST, SMTP_PORT)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.gmail_user, settings.gmail_app_password)
        server.sendmail(
            settings.gmail_user, [settings.recipient_email], msg.as_string()
        )

    logger.info("Email sent to %s", settings.recipient_email)
