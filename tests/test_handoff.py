from news_assistant.fetch import Candidate
from news_assistant.handoff import FetchResult, deliver


class _RecordingDrive:
    def __init__(self):
        self.written = None

    def write_fetch_payload(self, candidates):
        self.written = candidates


class _RecordingTrigger:
    def __init__(self):
        self.calls = []

    def fire(self, status, error=None):
        self.calls.append({"status": status, "error": error})


def _candidate(id_="1"):
    return Candidate(
        id=id_,
        title="New Python release",
        url="https://example.com",
        source="Hacker News",
        points=10,
        candidate_topics=["Python"],
    )


def test_deliver_writes_to_drive_and_fires_success_on_a_successful_fetch():
    drive = _RecordingDrive()
    trigger = _RecordingTrigger()
    result = FetchResult(candidates=[_candidate()])

    deliver(result, drive, trigger)

    assert drive.written == [_candidate()]
    assert trigger.calls == [{"status": "success", "error": None}]


def test_deliver_leaves_drive_untouched_and_fires_failure_on_a_failed_fetch():
    drive = _RecordingDrive()
    trigger = _RecordingTrigger()
    result = FetchResult(error="hn.algolia.com timed out")

    deliver(result, drive, trigger)

    assert drive.written is None
    assert trigger.calls == [{"status": "failure", "error": "hn.algolia.com timed out"}]
