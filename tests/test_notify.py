from news_assistant.notify import send_email


class _FakeResponse:
    ok = True


class _FakeSession:
    def __init__(self):
        self.post_calls = []

    def post(self, url, headers=None, json=None, timeout=None):
        self.post_calls.append({"url": url, "headers": headers, "json": json})
        return _FakeResponse()


def test_send_email_posts_to_resend_with_bearer_key():
    session = _FakeSession()

    send_email(
        subject="Today's Digest",
        body="AI/LLMs\n- Some item",
        to="user@example.com",
        sender="bot@example.com",
        api_key="re_test_key",
        session=session,
    )

    assert session.post_calls == [
        {
            "url": "https://api.resend.com/emails",
            "headers": {
                "Authorization": "Bearer re_test_key",
                "Content-Type": "application/json",
            },
            "json": {
                "from": "bot@example.com",
                "to": ["user@example.com"],
                "subject": "Today's Digest",
                "text": "AI/LLMs\n- Some item",
            },
        }
    ]
