"""
Orchestrator — runs the full pipeline:
  fetch → summarise → render → send
"""

from __future__ import annotations

import logging
import sys
import json
from datetime import datetime, timezone

from mr_postman.config import load_feeds
from mr_postman.fetch import fetch_all
from mr_postman.render import render_html
from mr_postman.send import send
from mr_postman.summarize import summarise

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("=== Mr. Postman starting ===")
    now = datetime.now(tz=timezone.utc)

    # 1. Fetch
    logger.info("Step 1/4 — Fetching feeds …")
    feeds = load_feeds()

    # TODO: there is parsing logic that might be broken
    items = fetch_all(feeds)
    if not items:
        raise RuntimeError("No feed items fetched — aborting.")

    # 2. Summarise
    logger.info("Step 2/4 — Summarising with GPT-4o …")
    digest = summarise(items)

    if not digest.stories:
        logger.warning("GPT-4o returned no stories — aborting.")
        sys.exit(1)

    logger.info("  → %d stories selected", len(digest.stories))

    # 3. Render
    logger.info("Step 3/4 — Rendering HTML email …")
    html_body = render_html(digest, date=now)

    # # 4. Send
    logger.info("Step 4/4 — Sending email …")
    send(html_body, date=now)

    logger.info("=== Done ===")


if __name__ == "__main__":
    main()
