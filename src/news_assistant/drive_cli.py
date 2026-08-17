"""CLI entry point invoked by the digest-generation skill's Fetch Payload
read step: prints the day's Fetch Payload JSON to stdout, reading Drive
credentials from the environment. Thin and untested, same as cli.py and
notify_cli.py — the tested core is drive.GoogleDriveClient."""

import json
import os
import sys

from .drive import GoogleDriveClient


def main() -> None:
    client = GoogleDriveClient(
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        file_id=os.environ["GOOGLE_DRIVE_FILE_ID"],
    )
    candidates = client.read_fetch_payload()
    json.dump(candidates, sys.stdout)


if __name__ == "__main__":
    main()
