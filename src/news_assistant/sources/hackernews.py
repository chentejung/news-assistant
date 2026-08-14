"""Hacker News source adapter, backed by the Algolia HN Search API."""

import requests

from ..fetch import RawItem

FRONT_PAGE_URL = "https://hn.algolia.com/api/v1/search?tags=front_page"


def fetch_hackernews(session=requests) -> list[RawItem]:
    response = session.get(FRONT_PAGE_URL, timeout=10)
    response.raise_for_status()
    hits = response.json().get("hits", [])

    items = []
    for hit in hits:
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
