# Developer setup: Vercel-triggered fetch with Drive handoff

End-to-end provisioning checklist for ADR-0005 / issue #2 (`vercel-fetch-migration.md`'s Phase 1). Follow in order — later steps depend on values from earlier ones. Nothing here is committed to git; every credential ends up as an env var on Vercel or on the Claude Code routine.

## 1. Google Cloud — API, consent scope, OAuth client, refresh token

Full detail (including the exact 403 gotchas and how to recover from them) is in [`google-oauth-setup.md`](./google-oauth-setup.md). Summary:

- [ ] Enable the Google Drive API on the Cloud project.
- [ ] Declare `.../auth/drive.file` on the OAuth consent screen's Data Access scopes.
- [ ] Create a Web-application OAuth client, redirect URI `https://developers.google.com/oauthplayground`.
- [ ] Mint a refresh token via the OAuth Playground using your own client credentials (not the Playground's default shared ones — those auto-revoke in 24h).
- [ ] Run `python3 scripts/create_drive_file.py` (reads `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`/`GOOGLE_REFRESH_TOKEN` from a local `.env`) to create the Fetch Payload file through this same identity, and note the printed file ID.

**Output of this step:** `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `GOOGLE_DRIVE_FILE_ID`.

## 2. Gmail — App Password for SMTP

- [ ] Enable 2-Step Verification on the Gmail account that will send the digest emails.
- [ ] Generate an App Password (Google Account → Security → 2-Step Verification → App passwords).

We use SMTP + an App Password instead of the Gmail API specifically because the Gmail API's OAuth "Testing" mode issues refresh tokens that expire every 7 days for sensitive scopes like `gmail.send` — see ADR-0005.

**Output of this step:** `SMTP_APP_PASSWORD` (and the Gmail address itself, for `SMTP_USERNAME`).

## 3. Claude Code — the routine's trigger and connector

- [ ] Add an **API trigger** to the existing routine; note the `/fire` URL and bearer token it gives you.
- [ ] Remove the routine's **old cron trigger** — the API trigger becomes the sole path in, so there's no double-run risk or a stale trigger retrying the now-removed direct-fetch code path.
- [ ] Enable/authenticate the **Google Drive MCP connector** on the routine itself. This is separate from any interactive chat session's own Drive connector auth — authenticating Drive in a chat session does not cover the routine.
- [ ] Set `SMTP_USERNAME`, `SMTP_APP_PASSWORD` (from step 2), and `DIGEST_TO` on the routine's **cloud Environment** (not a per-routine setting — [claude.ai/code](https://claude.ai/code) → cloud icon above the message box → environment selector → edit the environment this routine uses, `.env`-format vars). Anthropic's own docs state cloud environments have no dedicated secrets store — these vars are plaintext and shared across every routine using that environment. Acceptable for a scoped, revocable Gmail App Password; know this before putting anything more sensitive there.

**Output of this step:** `ROUTINE_TRIGGER_URL`, `ROUTINE_TRIGGER_TOKEN`.

## 4. Vercel — the project and its env vars

- [ ] Create a Vercel project, import this GitHub repo. Python runtime is auto-detected from `requirements.txt`.
- [ ] Set these six env vars on the Vercel project:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `GOOGLE_REFRESH_TOKEN`
  - `GOOGLE_DRIVE_FILE_ID`
  - `ROUTINE_TRIGGER_URL`
  - `ROUTINE_TRIGGER_TOKEN`
- [ ] Confirm `vercel.json`'s cron (`30 14 * * *`) shows up under the project's Cron Jobs tab after the first deploy. Hobby-tier cron only guarantees hour-level precision, not exact-minute — expected, not a bug.

## 5. First real test

Per `vercel-fetch-migration.md` Phase 3:

- [ ] Manually invoke the deployed function's URL once — confirm it writes to Drive and calls the trigger.
- [ ] POST a synthetic `{"status": "failure", "error": "test"}` body to the routine's API trigger directly — confirm it emails a failure notice and makes no git commit.
- [ ] Let one real scheduled run happen; confirm the digest, the git commit, and the success email all show up.

Once that passes, close out issue #2's blocked status.

## FAQ / Troubleshooting

Questions that came up while actually doing this setup, kept here so the next person (or future you) doesn't have to rediscover them.

**How does the code actually get deployed on each side?**
Vercel builds/deploys on every push to `main` via its GitHub integration — only `api/` and what it imports trigger a rebuild, thanks to monorepo path-detection, so a digest-only commit won't redeploy it. The Claude Code routine has no deploy step at all: it clones `main` fresh on every firing, so a skill change takes effect on the very next run, automatically.

**Where is `drive.file` configured in this repo?**
Nowhere — it's not code, it's the OAuth *scope* you select when minting the refresh token in step 1. See `google-oauth-setup.md`.

**What redirect URI does the Google OAuth client need?**
Exactly `https://developers.google.com/oauthplayground`, and only for the one-time token-minting step — it can be removed afterward.

**The access token in the token-exchange response expires — is that a problem?**
No. Only the refresh token needs saving. `GoogleDriveClient` and `scripts/create_drive_file.py` both mint a fresh access token from the refresh token on every call; nothing caches or reuses the short-lived one.

**Why did `scripts/create_drive_file.py` fail with `403 Forbidden`?**
Two likely causes, both now covered in `google-oauth-setup.md` step 1: the Google Drive API wasn't enabled on the Cloud project, or `drive.file` wasn't declared on the OAuth consent screen's Data Access scopes (requesting a scope at authorization time isn't the same as declaring it on the consent screen).

**I don't see the previously configured Claude Code routine — was it deleted?**
No — routines don't auto-delete or auto-disable from repeated failures, only one-off runs do. It was confirmed still present (and still running the old pre-ADR-0005 config) via `RemoteTrigger`/`/schedule list`. If it's not visible in the web UI, check you're logged into the same claude.ai account that created it.

**I don't see a Google Drive connector to connect.**
It's gated to Pro/Max/Team/Enterprise plans — not visible on Free. (Resolved once on Pro.) Separately worth knowing: Anthropic's own docs describe this connector as a *document* picker (Google Docs specifically; Sheets and other types are explicitly unsupported), which doesn't obviously cover reading an arbitrary `.json` file the way the routine's step 3 needs. **Untested as of this writing** — verify it during Phase 3's first real test before trusting it; the fallback is a REST-based read in `drive.py` mirroring the already-tested `write_fetch_payload`, using the same OAuth token.

**Can the Gmail connector send the email instead of SMTP?**
No — Anthropic's docs state it explicitly: *"Claude cannot create, send, or modify emails"* via that connector. It's read/search-only. SMTP + App Password (or the Gmail API, ruled out for its 7-day token expiry) are the only actual sending paths.

**Where do `SMTP_USERNAME`/`SMTP_APP_PASSWORD`/`DIGEST_TO` actually get set?**
Not on the routine itself — there's no per-routine env var field in the trigger API. They go on the routine's shared cloud **Environment** instead (see step 3 above). No dedicated secrets store exists for this yet; the vars are plaintext, shared across every routine using that environment.

**What values go in `SMTP_USERNAME` and `DIGEST_TO`?**
Both plain email addresses. `SMTP_USERNAME` is the Gmail address the App Password belongs to (also used as the `From` sender). `DIGEST_TO` is the recipient — typically the same address, unless the digest should land in a different inbox than the sending account.
