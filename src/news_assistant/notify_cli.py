"""CLI entry point invoked by the digest-generation skill's email step:
sends an email via Resend, reading the recipient and credentials from the
environment and the body from stdin. Thin and untested, same as cli.py —
the tested core is notify.send_email."""

import argparse
import os
import sys

from .notify import send_email


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    args = parser.parse_args()

    body = sys.stdin.read()
    send_email(
        subject=args.subject,
        body=body,
        to=os.environ["DIGEST_TO"],
        sender=os.environ.get("DIGEST_FROM", "Tech Trends Digest <onboarding@resend.dev>"),
        api_key=os.environ["RESEND_API_KEY"],
    )


if __name__ == "__main__":
    main()
