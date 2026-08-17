"""Sends the Scheduled Run's email notifications — the rendered Digest on
success, a failure notice otherwise — via SMTP with a Gmail App Password.
Chosen over the Gmail API to avoid OAuth's 7-day refresh-token expiry for
sensitive scopes like gmail.send, which would silently break an unattended
daily job (ADR-0005)."""

import smtplib
from email.message import EmailMessage
from typing import Protocol


class SMTPClient(Protocol):
    def send_message(self, msg: EmailMessage) -> None: ...


def send_email(subject: str, body: str, to: str, sender: str, smtp: SMTPClient) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(body)
    smtp.send_message(msg)


def connect(host: str, port: int, username: str, app_password: str) -> smtplib.SMTP:
    smtp = smtplib.SMTP(host, port, timeout=10)
    smtp.starttls()
    smtp.login(username, app_password)
    return smtp
