"""
Feed configuration and environment-based settings.

Feed list is loaded from feeds.json at the project root (gitignored).
In GitHub Actions, write the secret FEEDS_CONFIG (the JSON file contents)
to feeds.json before running the digest — see .github/workflows/digest.yml.

Runtime secrets (API keys, SMTP credentials) are validated at startup via
pydantic-settings. Set them in the environment or a local .env file.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import BaseModel

from pydantic_settings import BaseSettings, SettingsConfigDict

# WARN: this could break if the file structure changes
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FEEDS_FILE = _PROJECT_ROOT / "feeds.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    openai_api_key: str
    gmail_user: str
    gmail_app_password: str
    recipient_email: str

    openai_model: str = "gpt-4o"
    min_description_length: int = 100


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


@dataclass(frozen=True)
class Feed(BaseModel):
    name: str
    url: str
    region: Literal["poland", "europe", "us"]
    priority: Literal["high", "medium", "low"] = "low"


def load_feeds() -> list[Feed]:
    """Load feed definitions from feeds.json.

    Raises FileNotFoundError with a helpful message if the file is absent.
    """
    if not _FEEDS_FILE.exists():
        raise FileNotFoundError(
            f"feeds.json not found at {_FEEDS_FILE}. "
            "Create it locally (it is gitignored) or write the FEEDS_CONFIG "
            "secret to that path in CI before running."
        )
    with _FEEDS_FILE.open(encoding="utf-8") as fh:
        raw = json.load(fh)
    return [Feed.model_validate(entry) for entry in raw]


FEEDS: list[Feed] = load_feeds()
