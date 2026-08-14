"""CLI entry point invoked by the digest-generation skill: fetches and
pre-filters candidates, printing them as JSON to stdout."""

import argparse
import json
import sys
from dataclasses import asdict

from .fetch import fetch_candidates
from .sources.hackernews import fetch_hackernews, parse_front_page


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-json",
        metavar="PATH",
        help=(
            "Skip the live Hacker News request and pre-filter an already-fetched "
            "Algolia front-page payload read from this file instead. For "
            "environments where the network call itself is blocked (e.g. a "
            "sandbox egress policy) but the payload can still be obtained "
            "some other way."
        ),
    )
    args = parser.parse_args()

    if args.from_json:
        with open(args.from_json) as f:
            payload = json.load(f)
        adapter = lambda: parse_front_page(payload)  # noqa: E731
    else:
        adapter = fetch_hackernews

    candidates = fetch_candidates([adapter])
    json.dump([asdict(c) for c in candidates], sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
