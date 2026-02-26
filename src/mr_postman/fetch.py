"""
Fetch and parse RSS feeds, returning cleaned FeedItem objects.

Live-blog fragments are filtered out here based on
description length (from config).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Literal

import feedparser

from mr_postman.config import Feed, get_settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FeedItem(BaseModel):
    source_name: str
    region: str
    title: str
    description: str
    url: str
    published: datetime
    priority: Literal["high", "medium", "low"] = "low"


def _is_valid_entry(description: str, feed_name: str, title: str) -> bool:
    """Check if an entry is valid based on description length."""
    if len(description) < get_settings().min_description_length:
        logger.debug(
            "Skipping short item from %s: %r (desc len %d)",
            feed_name,
            title,
            len(description),
        )
        return False
    return True


def _is_recent(published: datetime | None) -> bool:
    """Return True if published is within the last 72 hours. Discard if None."""
    if published is None:
        logger.debug("Discarding item with missing publish date")
        return False
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=72)
    return published >= cutoff


def _parse_feed_entry(entry, feed: Feed) -> FeedItem | None:
    """Parse a single feed entry into a FeedItem."""
    title = getattr(entry, "title", "")
    description = getattr(entry, "summary", "")
    link = getattr(entry, "link", "")

    published_parsed = getattr(entry, "published_parsed", None)
    if not published_parsed:
        logger.debug("Entry missing published date: %r", title)
        return None

    if not _is_valid_entry(description, feed.name, title):
        return None

    published = datetime(*published_parsed[:6], tzinfo=timezone.utc)

    if not _is_recent(published):
        logger.debug("Skipping old/undated item from %s: %r", feed.name, title)
        return None

    return FeedItem(
        source_name=feed.name,
        region=feed.region,
        title=title,
        description=description,
        url=link,
        published=published,
        priority=feed.priority,
    )


def fetch_feed(feed: Feed) -> list[FeedItem]:
    """Fetch a single RSS feed and return a filtered list of FeedItems."""
    logger.info("Fetching %s …", feed.name)
    try:
        parsed = feedparser.parse(feed.url)
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", feed.name, exc)
        return []

    if parsed.bozo and parsed.bozo_exception:
        logger.warning(
            "Feed %s had parse warning: %s", feed.name, parsed.bozo_exception
        )

    items: list[FeedItem] = []
    for entry in parsed.entries:
        item = _parse_feed_entry(entry, feed)
        if item:
            items.append(item)

    logger.info(
        "  → %d usable items out of %d from %s",
        len(items),
        len(parsed.entries),
        feed.name,
    )
    return items


def fetch_all(feeds: list[Feed]) -> list[FeedItem]:
    all_items: list[FeedItem] = []

    for feed in feeds:
        for item in fetch_feed(feed):
            all_items.append(item)

    logger.info("Total items fetched across all feeds: %d", len(all_items))
    return all_items
