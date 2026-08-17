from news_assistant.trigger import RoutineTrigger


class _FakeResponse:
    def raise_for_status(self):
        pass


class _FakeSession:
    def __init__(self):
        self.post_calls = []

    def post(self, url, headers=None, json=None, timeout=None):
        self.post_calls.append({"url": url, "headers": headers, "json": json})
        return _FakeResponse()


def test_fire_posts_success_status_with_bearer_token():
    session = _FakeSession()
    trigger = RoutineTrigger(url="https://example.com/fire", bearer_token="tok", session=session)

    trigger.fire(status="success")

    assert session.post_calls == [
        {
            "url": "https://example.com/fire",
            "headers": {"Authorization": "Bearer tok"},
            "json": {"status": "success"},
        }
    ]


def test_fire_posts_failure_status_with_error():
    session = _FakeSession()
    trigger = RoutineTrigger(url="https://example.com/fire", bearer_token="tok", session=session)

    trigger.fire(status="failure", error="hn.algolia.com timed out")

    assert session.post_calls == [
        {
            "url": "https://example.com/fire",
            "headers": {"Authorization": "Bearer tok"},
            "json": {"status": "failure", "error": "hn.algolia.com timed out"},
        }
    ]
