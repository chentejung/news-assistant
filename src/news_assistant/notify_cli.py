"""CLI entry point invoked by the digest-generation skill's email step:
sends an email via SMTP, reading the recipient and credentials from the
environment and the body from stdin. Thin and untested, same as cli.py —
the tested core is notify.send_email/connect."""

import argparse
import os
import sys

from .notify import connect, send_email


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    args = parser.parse_args()

    body = sys.stdin.read()
    username = os.environ["SMTP_USERNAME"]
    smtp = connect(
        host=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        port=int(os.environ.get("SMTP_PORT", "587")),
        username=username,
        app_password=os.environ["SMTP_APP_PASSWORD"],
    )
    try:
        send_email(
            subject=args.subject,
            body=body,
            to=os.environ["DIGEST_TO"],
            sender=username,
            smtp=smtp,
        )
    finally:
        smtp.quit()


if __name__ == "__main__":
    main()
