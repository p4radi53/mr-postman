"""
Call LLM to curate and summarise the top stories from fetched feed items.
"""

from __future__ import annotations

import logging

import instructor
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal

from mr_postman.config import get_settings
from mr_postman.fetch import FeedItem

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are an experienced international news editor producing a concise daily digest \
for a politically engaged reader who follows Poland, Europe, and the United States. \
Your analysis should be balanced — neither neoliberal nor nationalist in framing — \
and should include geopolitical, socio-economic, and democratic-governance perspectives \
where relevant. You write in clear, neutral journalistic English.
"""

USER_PROMPT_TEMPLATE = """\
Below is today's raw feed data from {n_items} news items across {n_sources} sources.
---

{items_block}

---

Your task:
1. Select exactly 5 stories from Poland, 5 stories from Europe, and 3 stories from the \
United States. Prioritise stories that:
   - Have clear political, geopolitical, or socio-economic significance
   - Are substantive news (not opinion fluff, not live-blog fragments, not sports/entertainment)
   - Use priority as a hint, but apply your editorial judgement to select the most important stories overall.
The higher priority sources should have better quality content.
2. For each story write a 2-3 sentence neutral summary in English (translate Polish items).
"""


class Story(BaseModel):
    rank: int
    headline: str
    summary: str
    source_name: str
    region: Literal["poland", "europe", "us"]
    url: str
    tags: list[str]


class DigestSummary(BaseModel):
    stories: list[Story]


def _build_items_block(items: list[FeedItem]) -> str:
    return "\n---\n".join([item.model_dump_json() for item in items])


def summarise(items: list[FeedItem]) -> DigestSummary:
    settings = get_settings()
    client = instructor.from_openai(OpenAI(api_key=settings.openai_api_key))

    source_names = {item.source_name for item in items}
    items_block = _build_items_block(items)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        n_items=len(items),
        n_sources=len(source_names),
        items_block=items_block,
    )

    logger.info(
        "Sending %d items to %s for summarisation …", len(items), settings.openai_model
    )

    return client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        response_model=DigestSummary,
    )
