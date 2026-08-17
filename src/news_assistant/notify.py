"""Sends the Scheduled Run's email notifications — the rendered Digest on
success, a failure notice otherwise — via the Resend HTTP API. SMTP was
ruled out: a real routine run confirmed the cloud sandbox only permits an
HTTPS proxy path, not raw TCP sockets, so smtplib's socket connection
failed outright regardless of credentials. Resend needs only a static API
key over plain HTTPS — no OAuth lifecycle, unlike the Gmail API's
sensitive-scope token expiry (ADR-0005)."""

import requests

RESEND_URL = "https://api.resend.com/emails"


def send_email(subject: str, body: str, to: str, sender: str, api_key: str, session=requests) -> None:
    response = session.post(
        RESEND_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={"from": sender, "to": [to], "subject": subject, "text": body},
        timeout=10,
    )
    if not response.ok:
        raise RuntimeError(f"Resend send failed ({response.status_code}): {response.text}")
