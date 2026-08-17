from api.index import run
from news_assistant.fetch import RawItem


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


def test_run_delivers_candidates_on_a_successful_fetch():
    drive = _RecordingDrive()
    trigger = _RecordingTrigger()
    adapter = lambda: [  # noqa: E731
        RawItem(
            id="hn:1",
            title="New Python release",
            url="https://example.com",
            source="Hacker News",
            points=10,
        )
    ]

    result = run(adapters=[adapter], drive=drive, trigger=trigger)

    assert result.success
    assert drive.written[0].title == "New Python release"
    assert trigger.calls == [{"status": "success", "error": None}]


def test_run_delivers_a_failure_when_the_adapter_raises():
    drive = _RecordingDrive()
    trigger = _RecordingTrigger()

    def failing_adapter():
        raise RuntimeError("hn.algolia.com timed out")

    result = run(adapters=[failing_adapter], drive=drive, trigger=trigger)

    assert not result.success
    assert result.error == "hn.algolia.com timed out"
    assert drive.written is None
    assert trigger.calls == [{"status": "failure", "error": "hn.algolia.com timed out"}]
