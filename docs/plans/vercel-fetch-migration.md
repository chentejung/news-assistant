# Migration: Vercel-triggered fetch with Google Drive handoff

Implementation plan for the pivot recorded in [ADR-0005](../adr/0005-vercel-fetch-with-drive-handoff.md) and tracked in [issue #2](https://github.com/chentejung/news-assistant/issues/2). This is a working plan, not a decision record — see the ADR for the *why*.

## Problem

The Claude Code cloud routine's sandbox blocks outbound HTTP to `hn.algolia.com` regardless of network policy setting, so the routine can't fetch Hacker News data directly (issue #2). The fetch moves to a Vercel serverless function instead, with Google Drive as the handoff point.

## Repo structure

One repo, two execution surfaces reading from it — not two repos:

```
news-assistant/
├── CONTEXT.md
├── docs/
│   ├── adr/
│   └── plans/
├── src/
│   └── news_assistant/          # existing fetch + pre-filter (Python) — unchanged, single source of truth
├── api/
│   └── index.py                 # Vercel Function entry point: imports src/news_assistant,
│                                 #   writes Fetch Payload to Drive, POSTs the API trigger
├── vercel.json                  # cron schedule (~daily) + Python runtime config, root dir
├── requirements.txt
├── digests/                     # committed Digest markdown — unchanged
└── .claude/
    └── skills/tech-trends-digest/   # the routine's skill: reads Fetch Payload via Drive MCP,
                                       classifies/summarizes/renders/commits/emails
```

- **Vercel** connects to this GitHub repo via its own integration and only builds/deploys `api/` (plus whatever it imports from `src/news_assistant/`). Every push to `main` triggers a Production deployment automatically; Vercel Cron only fires against Production. Monorepo path-detection means a commit that only touches `digests/` or `.claude/skills/` won't trigger a rebuild.
- **The Claude Code cloud routine** clones the repo fresh from `main` on every firing — no snapshotting, no separate deploy step. A change to `SKILL.md` takes effect on the next firing automatically. Branch is controlled by the routine's saved prompt (defaults to `main`), not a separate config field.
- `src/news_assistant/` stays the single implementation of fetch + pre-filter; `api/index.py` is a thin Vercel wrapper around it, not a duplicate.

## Pipeline

1. Vercel Function (`api/index.py`) runs on a daily Vercel Cron schedule (Hobby tier: once/day max, ±59 min precision — accepted as fine).
2. It runs the existing fetch + keyword pre-filter logic.
3. On success: writes the result — the **Fetch Payload** — to a single well-known file in Google Drive, overwriting the previous day's (`drive.file`-scoped OAuth token, stored as a Vercel secret).
4. Either way (success or failure): `POST`s the routine's **API trigger** (`/fire` endpoint, bearer token) with an explicit `{status: "success"|"failure", payload | error}` body — the routine never infers status from Drive file state. On failure, Drive is left untouched.
5. The routine's own cron trigger is removed; the API trigger is the sole path in.
6. On success: the routine reads the Fetch Payload via its Google Drive MCP connector (MCP traffic routes through Anthropic's backend, not the sandbox's network boundary, so it isn't subject to the egress block that blocked the direct fetch), classifies, summarizes, renders the Digest, commits it to git (unchanged from the original ACs), and emails the full rendered content inline via SMTP + a Gmail App Password.
7. On failure: no git commit — nothing fits the Digest definition — but the routine still sends a failure-notice email.

## Implementation phases

### Phase 1 — External provisioning (manual, dashboard/CLI)

1. Vercel: create/link a project to this repo (Python runtime for `api/` is auto-detected via `requirements.txt`).
2. Google Cloud: create an OAuth client, generate a refresh token scoped to `drive.file`.
3. Google Drive: manually create one empty file (e.g. `fetch-payload.json`) — `GoogleDriveClient.write_fetch_payload` does a `PATCH` (update), not a create, so the file must exist before the first run. Note its file ID from the Drive URL.
4. Set these as Vercel project env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `GOOGLE_DRIVE_FILE_ID` (from step 3), `ROUTINE_TRIGGER_URL`, `ROUTINE_TRIGGER_TOKEN` (from step 6).
5. Gmail: enable 2-Step Verification, generate an App Password.
6. Claude Code: add an API trigger to the existing routine (note its URL + bearer token for step 4), remove its old cron trigger, and enable/authenticate the Google Drive MCP connector on the routine (routine-level connector auth is separate from any interactive session's — this session authenticating Drive does not cover the routine).
7. Set these as env vars in the routine's own environment (not Vercel's): `SMTP_USERNAME` (the Gmail address), `SMTP_APP_PASSWORD` (from step 5), `DIGEST_TO` (where the digest should be emailed — likely the same address). `SMTP_HOST`/`SMTP_PORT` default to `smtp.gmail.com`/`587` and don't need setting.

### Phase 2 — Code

5. `api/index.py`: wraps `src/news_assistant/`, writes Fetch Payload to Drive on success, POSTs the API trigger either way.
6. `vercel.json`: daily cron schedule, Python runtime, root config.
7. Update `tech-trends-digest` skill: read Fetch Payload via Drive MCP, branch on success/failure, add the SMTP email-send step, keep git-commit gated to success only.

### Phase 3 — Testing

8. Local unit test of `api/index.py` against the existing fetch/pre-filter test suite.
9. Vercel preview deploy — manually hit the function URL once, confirm it writes to Drive and calls the trigger.
10. Manually POST a synthetic failure payload to the API trigger, confirm the routine emails a failure notice and skips the git commit.
11. Let one real end-to-end run happen on schedule; confirm the digest, the commit, and the email all show up.

### Phase 4 — Cutover

12. Once a real run succeeds end-to-end, close out issue #2's blocked status.

## Open items

- Phase 1 steps require manual dashboard work; a wizard-style walkthrough can be generated on request.
- No preview-environment equivalent exists for dry-running a routine skill change before merge — testing a skill change means either an interactive session against a branch, or merging to `main` and firing the routine on-demand via the API trigger.
