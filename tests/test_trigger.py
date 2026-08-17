from news_assistant.trigger import RoutineTrigger


class _FakeResponse:
    ok = True


class _FakeSession:
    def __init__(self):
        self.post_calls = []

    def post(self, url, headers=None, json=None, timeout=None):
        self.post_calls.append({"url": url, "headers": headers, "json": json})
        return _FakeResponse()


def test_fire_sends_success_text_with_required_headers():
    session = _FakeSession()
    trigger = RoutineTrigger(url="https://example.com/fire", bearer_token="tok", session=session)

    trigger.fire(status="success")

    assert session.post_calls == [
        {
            "url": "https://example.com/fire",
            "headers": {
                "Authorization": "Bearer tok",
                "anthropic-beta": "experimental-cc-routine-2026-04-01",
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            "json": {"text": "Fetch succeeded."},
        }
    ]


def test_fire_sends_failure_text_with_the_error_message():
    session = _FakeSession()
    trigger = RoutineTrigger(url="https://example.com/fire", bearer_token="tok", session=session)

    trigger.fire(status="failure", error="hn.algolia.com timed out")

    assert session.post_calls[0]["json"] == {
        "text": "Fetch failed: hn.algolia.com timed out"
    }
