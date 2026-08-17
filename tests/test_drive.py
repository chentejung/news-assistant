import json

from news_assistant.drive import GoogleDriveClient
from news_assistant.fetch import Candidate


class _FakeResponse:
    ok = True

    def __init__(self, payload=None):
        self._payload = payload or {}

    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self, get_payload=None):
        self.post_calls = []
        self.patch_calls = []
        self.get_calls = []
        self._get_payload = get_payload or []

    def post(self, url, data=None, timeout=None):
        self.post_calls.append({"url": url, "data": data})
        return _FakeResponse({"access_token": "fake-token"})

    def patch(self, url, headers=None, data=None, timeout=None):
        self.patch_calls.append({"url": url, "headers": headers, "data": data})
        return _FakeResponse()

    def get(self, url, headers=None, timeout=None):
        self.get_calls.append({"url": url, "headers": headers})
        return _FakeResponse(self._get_payload)


def _candidate():
    return Candidate(
        id="hn:1",
        title="New Python release",
        url="https://example.com",
        source="Hacker News",
        points=10,
        candidate_topics=["Python"],
    )


def test_write_fetch_payload_exchanges_refresh_token_and_uploads_candidates_json():
    session = _FakeSession()
    client = GoogleDriveClient(
        client_id="client-id",
        client_secret="client-secret",
        refresh_token="refresh-token",
        file_id="file-123",
        session=session,
    )

    client.write_fetch_payload([_candidate()])

    assert session.post_calls == [
        {
            "url": "https://oauth2.googleapis.com/token",
            "data": {
                "client_id": "client-id",
                "client_secret": "client-secret",
                "refresh_token": "refresh-token",
                "grant_type": "refresh_token",
            },
        }
    ]
    assert len(session.patch_calls) == 1
    patch_call = session.patch_calls[0]
    assert (
        patch_call["url"]
        == "https://www.googleapis.com/upload/drive/v3/files/file-123?uploadType=media"
    )
    assert patch_call["headers"]["Authorization"] == "Bearer fake-token"
    assert patch_call["headers"]["Content-Type"] == "application/json"
    assert json.loads(patch_call["data"]) == [
        {
            "id": "hn:1",
            "title": "New Python release",
            "url": "https://example.com",
            "source": "Hacker News",
            "points": 10,
            "candidate_topics": ["Python"],
        }
    ]


def test_read_fetch_payload_exchanges_refresh_token_and_downloads_file_content():
    payload = [{"id": "hn:1", "title": "New Python release"}]
    session = _FakeSession(get_payload=payload)
    client = GoogleDriveClient(
        client_id="client-id",
        client_secret="client-secret",
        refresh_token="refresh-token",
        file_id="file-123",
        session=session,
    )

    result = client.read_fetch_payload()

    assert result == payload
    assert len(session.get_calls) == 1
    get_call = session.get_calls[0]
    assert get_call["url"] == "https://www.googleapis.com/drive/v3/files/file-123?alt=media"
    assert get_call["headers"]["Authorization"] == "Bearer fake-token"
