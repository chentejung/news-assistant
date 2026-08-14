"""Hacker News source adapter, backed by the Algolia HN Search API."""

import requests

from ..fetch import RawItem

FRONT_PAGE_URL = "https://hn.algolia.com/api/v1/search?tags=front_page"


def fetch_hackernews(session=requests) -> list[RawItem]:
    response = session.get(FRONT_PAGE_URL, timeout=10)
    response.raise_for_status()
    return parse_front_page(response.json())


def parse_front_page(payload: dict) -> list[RawItem]:
    """Map an already-fetched Algolia front-page payload (the same shape
    `fetch_hackernews` gets from the network) to RawItems. Split out so a
    caller that fetched the payload through some other channel — e.g. a
    sandbox whose network policy blocks calling the API directly — can
    still run it through the same mapping logic."""
    items = []
    for hit in payload.get("hits", []):
        title = hit.get("title")
        if not title:
            continue
        object_id = hit["objectID"]
        items.append(
            RawItem(
                id=f"hn:{object_id}",
                title=title,
                url=hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}",
                source="Hacker News",
                points=hit.get("points", 0),
            )
        )
    return items
