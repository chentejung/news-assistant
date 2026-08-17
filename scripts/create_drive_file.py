#!/usr/bin/env python3
"""One-off provisioning script (not used at runtime): creates the single
Fetch Payload file in Google Drive using the same OAuth-authorized identity
that minted the refresh token, so the file is guaranteed visible to a
drive.file-scoped token — a file created by hand in the Drive web UI may
not be, since that scope only sees files this OAuth client itself created.
See docs/plans/google-oauth-setup.md. Prints the new file's ID; set that as
GOOGLE_DRIVE_FILE_ID.

Usage (reads GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REFRESH_TOKEN
from a .env file at the repo root if present, without overriding any
already set in the real environment):
    python3 scripts/create_drive_file.py
"""

import os
from pathlib import Path

import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
CREATE_URL = "https://www.googleapis.com/drive/v3/files"


def load_dotenv(path: Path = Path(__file__).resolve().parent.parent / ".env") -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.removeprefix("export ").partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def main() -> None:
    load_dotenv()
    client_id = os.environ["GOOGLE_CLIENT_ID"]
    client_secret = os.environ["GOOGLE_CLIENT_SECRET"]
    refresh_token = os.environ["GOOGLE_REFRESH_TOKEN"]

    token_response = requests.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=10,
    )
    if not token_response.ok:
        raise SystemExit(f"Token exchange failed ({token_response.status_code}): {token_response.text}")
    access_token = token_response.json()["access_token"]

    create_response = requests.post(
        CREATE_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": "fetch-payload.json", "mimeType": "application/json"},
        timeout=10,
    )
    if not create_response.ok:
        raise SystemExit(f"File creation failed ({create_response.status_code}): {create_response.text}")
    file_id = create_response.json()["id"]

    print(f"Created fetch-payload.json — set GOOGLE_DRIVE_FILE_ID={file_id}")


if __name__ == "__main__":
    main()
