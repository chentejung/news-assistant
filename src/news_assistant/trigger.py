"""Calls the Scheduled Run routine's API trigger (ADR-0005) — the sole path
that starts a run now that the routine's own cron trigger is removed.

The /fire endpoint takes no structured status field — its only body field
is a single freeform `text` string, injected as initial context alongside
the routine's saved prompt (not parsed as JSON, not validated against any
schema). So the authoritative success/failure signal is encoded as a plain
sentence the routine's own prompt is written to recognize, not as a JSON
contract. It also requires the anthropic-beta and anthropic-version headers
below — omitting them, not the body shape, is what produces a 400."""

import requests

ANTHROPIC_BETA = "experimental-cc-routine-2026-04-01"
ANTHROPIC_VERSION = "2023-06-01"


class RoutineTrigger:
    def __init__(self, url, bearer_token, session=requests):
        self._url = url
        self._bearer_token = bearer_token
        self._session = session

    def fire(self, status: str, error: str | None = None) -> None:
        text = "Fetch succeeded." if status == "success" else f"Fetch failed: {error}"
        response = self._session.post(
            self._url,
            headers={
                "Authorization": f"Bearer {self._bearer_token}",
                "anthropic-beta": ANTHROPIC_BETA,
                "anthropic-version": ANTHROPIC_VERSION,
                "Content-Type": "application/json",
            },
            json={"text": text},
            timeout=10,
        )
        if not response.ok:
            raise RuntimeError(
                f"Routine trigger failed ({response.status_code}): {response.text}"
            )
