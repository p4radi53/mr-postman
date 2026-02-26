# mr-postman

A fully automated daily political news digest delivered by email.

Mr. Postman fetches articles from a curated set of RSS political feeds, uses LLM to editorially select and summarise the top stories, renders them into a styled HTML email, and delivers the digest via Gmail SMTP — every morning.

## How it works

1. **Fetch** — Loads RSS feeds from `feeds.json`, filters out short or stale articles
2. **Summarise** — Sends the articles to the LLM
3. **Render** — Renders a responsive HTML email via Jinja2
4. **Send** — Delivers the email via Gmail SMTP (port 587, STARTTLS)

## Requirements

- Python 3.13
- [`uv`](https://docs.astral.sh/uv/) package manager
- An OpenAI API key
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords)

## Setup

Clone the repo, install packages using `uv sync` and create a `feeds.json` file in the project root.

## Running

```bash
uv run mr-postman
```

### feeds.json

An array of RSS feed objects:

```json
[
  {
    "name": "BBC Europe",
    "url": "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "region": "europe",
    "language": "en",
    "priority": "low"
  }
]
```

## Automation

A GitHub Actions workflow scheduled using CRON. It can also be triggered manually via the Actions tab.
