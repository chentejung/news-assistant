from news_assistant.notify import send_email


class _RecordingSMTP:
    def __init__(self):
        self.sent = None

    def send_message(self, msg):
        self.sent = msg


def test_send_email_composes_and_sends_the_message():
    smtp = _RecordingSMTP()

    send_email(
        subject="Today's Digest",
        body="AI/LLMs\n- Some item",
        to="user@example.com",
        sender="bot@example.com",
        smtp=smtp,
    )

    assert smtp.sent["Subject"] == "Today's Digest"
    assert smtp.sent["From"] == "bot@example.com"
    assert smtp.sent["To"] == "user@example.com"
    assert smtp.sent.get_content().strip() == "AI/LLMs\n- Some item"
