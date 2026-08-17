"""Calls the Scheduled Run routine's API trigger (ADR-0005) — the sole path
that starts a run now that the routine's own cron trigger is removed. The
call itself carries the authoritative success/failure status; the routine
never infers status from Drive file state."""

import requests


class RoutineTrigger:
    def __init__(self, url, bearer_token, session=requests):
        self._url = url
        self._bearer_token = bearer_token
        self._session = session

    def fire(self, status: str, error: str | None = None) -> None:
        body = {"status": status}
        if error is not None:
            body["error"] = error
        response = self._session.post(
            self._url,
            headers={"Authorization": f"Bearer {self._bearer_token}"},
            json=body,
            timeout=10,
        )
        response.raise_for_status()
