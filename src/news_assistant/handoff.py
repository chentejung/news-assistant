"""Hands a day's fetch result off to the Scheduled Run (ADR-0005): writes the
Fetch Payload to Drive on success, and always calls the routine's API
trigger with an explicit status — the routine never infers success or
failure from Drive file state, so a failed fetch can't be mistaken for a
successful one with no new data. On failure, Drive is left untouched."""

from dataclasses import dataclass
from typing import Protocol

from .fetch import Candidate


@dataclass
class FetchResult:
    """Either candidates from a successful fetch, or an error from a failed one."""

    candidates: list[Candidate] | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


class DriveClient(Protocol):
    def write_fetch_payload(self, candidates: list[Candidate]) -> None: ...


class TriggerClient(Protocol):
    def fire(self, status: str, error: str | None = None) -> None: ...


def deliver(result: FetchResult, drive: DriveClient, trigger: TriggerClient) -> None:
    if result.success:
        drive.write_fetch_payload(result.candidates)
        trigger.fire(status="success")
    else:
        trigger.fire(status="failure", error=result.error)
