"""The fetch script's single public entry point (the test seam): pulls raw
items from a list of source adapters and pre-filters them against the fixed
Topic list."""

from dataclasses import dataclass, field
from typing import Callable

from .topics import match_topics


@dataclass
class RawItem:
    id: str
    title: str
    url: str
    source: str
    points: int = 0


@dataclass
class Candidate:
    id: str
    title: str
    url: str
    source: str
    points: int
    candidate_topics: list[str] = field(default_factory=list)


SourceAdapter = Callable[[], list[RawItem]]


def fetch_candidates(adapters: list[SourceAdapter]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for adapter in adapters:
        for item in adapter():
            topics = match_topics(item.title)
            if not topics:
                continue
            candidates.append(
                Candidate(
                    id=item.id,
                    title=item.title,
                    url=item.url,
                    source=item.source,
                    points=item.points,
                    candidate_topics=topics,
                )
            )
    return candidates
