"""
Render the HTML email from a DigestSummary using Jinja2.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from mr_postman.summarize import DigestSummary

logger = logging.getLogger(__name__)

# Resolve templates directory relative to the project root
_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"


_REGION_ORDER = ["poland", "europe", "us"]


def render_html(digest: DigestSummary, date: datetime | None = None) -> str:
    """Render the digest as an HTML string suitable for an email body."""
    if date is None:
        date = datetime.now(tz=timezone.utc)

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
    )

    stories = sorted(
        digest.stories,
        key=lambda s: (_REGION_ORDER.index(s.region), s.rank),
    )

    template = env.get_template("digest.html.j2")
    html = template.render(
        stories=stories,
        date=date,
    )
    logger.info("Rendered HTML email (%d bytes)", len(html))
    return html
