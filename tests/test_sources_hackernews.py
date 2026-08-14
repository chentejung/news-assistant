from news_assistant.sources.hackernews import fetch_hackernews


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self, payload):
        self._payload = payload

    def get(self, url, timeout=None):
        return _FakeResponse(self._payload)


def test_fetch_hackernews_maps_hits_to_raw_items():
    payload = {
        "hits": [
            {
                "objectID": "111",
                "title": "New Python release ships faster startup",
                "url": "https://python.org/news",
                "points": 42,
            }
        ]
    }
    session = _FakeSession(payload)

    items = fetch_hackernews(session=session)

    assert len(items) == 1
    item = items[0]
    assert item.id == "hn:111"
    assert item.title == "New Python release ships faster startup"
    assert item.url == "https://python.org/news"
    assert item.source == "Hacker News"
    assert item.points == 42


def test_fetch_hackernews_falls_back_to_hn_discussion_url_when_no_external_url():
    payload = {"hits": [{"objectID": "222", "title": "Ask HN: best SRE books?", "points": 7}]}
    session = _FakeSession(payload)

    items = fetch_hackernews(session=session)

    assert items[0].url == "https://news.ycombinator.com/item?id=222"


def test_fetch_hackernews_skips_hits_without_a_title():
    payload = {"hits": [{"objectID": "333", "points": 1}]}
    session = _FakeSession(payload)

    items = fetch_hackernews(session=session)

    assert items == []
