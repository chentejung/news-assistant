"""Vercel Function entry point (ADR-0005): runs on a daily cron schedule,
fetches + pre-filters candidates via the existing news_assistant fetch
script, and hands the result off to the Scheduled Run via Google Drive plus
its API trigger. Kept thin and untested — the real logic lives in
news_assistant.handoff/drive/trigger, which are unit tested directly."""

import os
from http.server import BaseHTTPRequestHandler

from news_assistant.drive import GoogleDriveClient
from news_assistant.fetch import fetch_candidates
from news_assistant.handoff import FetchResult, deliver
from news_assistant.sources.hackernews import fetch_hackernews
from news_assistant.trigger import RoutineTrigger


def run(adapters=None, drive=None, trigger=None) -> FetchResult:
    if adapters is None:
        adapters = [fetch_hackernews]
    if drive is None:
        drive = GoogleDriveClient(
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
            refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
            file_id=os.environ["GOOGLE_DRIVE_FILE_ID"],
        )
    if trigger is None:
        trigger = RoutineTrigger(
            url=os.environ["ROUTINE_TRIGGER_URL"],
            bearer_token=os.environ["ROUTINE_TRIGGER_TOKEN"],
        )

    try:
        candidates = fetch_candidates(adapters)
        result = FetchResult(candidates=candidates)
    except Exception as exc:
        # A failed fetch still has to notify the routine explicitly (ADR-0005) —
        # this is the system boundary, not a scenario we can validate away.
        result = FetchResult(error=str(exc))

    deliver(result, drive, trigger)
    return result


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        result = run()
        self.send_response(200 if result.success else 502)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok" if result.success else result.error.encode("utf-8"))
