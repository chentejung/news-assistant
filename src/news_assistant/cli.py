"""CLI entry point invoked by the digest-generation skill: fetches and
pre-filters candidates, printing them as JSON to stdout."""

import json
import sys
from dataclasses import asdict

from .fetch import fetch_candidates
from .sources.hackernews import fetch_hackernews


def main() -> None:
    candidates = fetch_candidates([fetch_hackernews])
    json.dump([asdict(c) for c in candidates], sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
