"""Google Drive client for the Fetch Payload handoff (ADR-0005): overwrites
a single well-known file each run — Drive is a transient handoff buffer,
not a durable store, so there's no history to preserve. Uses a
drive.file-scoped OAuth refresh token, exchanged for a fresh access token on
each call since Vercel functions are stateless."""

import json
from dataclasses import asdict

import requests

from .fetch import Candidate

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"


class GoogleDriveClient:
    def __init__(self, client_id, client_secret, refresh_token, file_id, session=requests):
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._file_id = file_id
        self._session = session

    def _access_token(self) -> str:
        response = self._session.post(
            TOKEN_URL,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def write_fetch_payload(self, candidates: list[Candidate]) -> None:
        token = self._access_token()
        body = json.dumps([asdict(c) for c in candidates]).encode("utf-8")
        response = self._session.patch(
            UPLOAD_URL.format(file_id=self._file_id),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            data=body,
            timeout=10,
        )
        response.raise_for_status()
