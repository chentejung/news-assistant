# Google OAuth setup for the Drive handoff

One-time provisioning steps for the `drive.file`-scoped refresh token `api/index.py` uses to write the Fetch Payload (ADR-0005, Phase 1 of `vercel-fetch-migration.md`). Do this once; the resulting refresh token is long-lived.

## 1. Enable the Drive API and declare the scope

Two easy-to-miss project-level settings that aren't part of creating credentials, and that a 403 at the API-call step (not the OAuth step) usually traces back to:

- **Enable the API itself.** Cloud Console → **APIs & Services** → **Library** → search "Google Drive API" → **Enable**. Creating OAuth credentials does *not* enable the API — they're separate steps. Skipping this produces a 403 whose body says something like `"Drive API has not been used in project ... before or it is disabled"`.
- **Declare the scope on the OAuth consent screen.** Cloud Console → **APIs & Services** → **OAuth consent screen** → **Data Access** → **Add or Remove Scopes** → add `.../auth/drive.file` explicitly here, not just checked later in the Playground. An app can request a scope at authorization time that isn't declared on its own consent screen, and Google rejects the resulting API calls.

## 2. Create the OAuth client

Google Cloud Console → **Credentials** → **Create Credentials** → **OAuth client ID**.

- **Application type:** Web application (not Desktop — the Playground flow below needs a web-type client with a redirect URI).
- **Authorized redirect URIs:** add exactly

  ```
  https://developers.google.com/oauthplayground
  ```

  This is only needed for the one-time token-minting step below; it can be removed afterward (Google requires at least one redirect URI to remain, so don't remove it down to zero).

Note the **Client ID** and **Client Secret** — these become `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` later.

## 3. Mint the refresh token via OAuth Playground

Use the [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/), not a fully manual flow — Google deprecated the out-of-band (`urn:ietf:wg:oauth:2.0:oob`) redirect for new clients, so this is the practical path for a one-off personal-project token.

1. Gear icon (top right) → check **"Use your own OAuth credentials"** → paste in the Client ID and Client Secret from step 2.

   This matters beyond just using your own client: the Playground's *default* shared credentials auto-revoke refresh tokens after 24 hours. With your own credentials, that expiry doesn't apply — the same class of trap as the Gmail API's 7-day sensitive-scope token expiry we avoided by using SMTP instead (ADR-0005).

2. In the scope list, find **Drive API v3**, check `https://www.googleapis.com/auth/drive.file`. Don't select a broader Drive scope — the whole point is limiting the token to files this OAuth client itself creates.
3. **Authorize APIs** → sign in with the Google account whose Drive you want to use → consent.
4. **Exchange authorization code for tokens** → the response body is JSON containing `access_token`, `refresh_token`, `expires_in`, `scope`, `token_type`.

**Treat both tokens as secrets from this point on** — don't paste them into chat logs, commit them, or post them anywhere. The `access_token` is short-lived (~1 hour) and disposable — nothing here reuses it. The `refresh_token` is the one that matters long-term; it becomes `GOOGLE_REFRESH_TOKEN`.

## 4. Create the Fetch Payload file through this same identity

`GoogleDriveClient.write_fetch_payload` (`src/news_assistant/drive.py`) does a `PATCH` — it updates an existing file, it doesn't create one. The file has to exist before the first Vercel run, **and** it has to be visible to the `drive.file`-scoped token, which only sees files *this OAuth client* created. A file made by hand in the regular Drive web UI under your own login may not qualify.

Put `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN` in a `.env` file at the repo root (already `.gitignore`d), then run:

```
python3 scripts/create_drive_file.py
```

It exchanges the refresh token for its own fresh access token (never reusing the one from step 3) and creates `fetch-payload.json` via the Drive API. On failure it prints the response body verbatim — Google's actual error message — rather than just a bare status code, so a 403 here is self-diagnosing back to step 1's two settings.

It prints the new file's ID on success — that becomes `GOOGLE_DRIVE_FILE_ID`.

## 5. What you should have after this

Four values, all destined for Vercel project env vars (never committed):

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`
- `GOOGLE_DRIVE_FILE_ID`

See `vercel-fetch-migration.md`'s Phase 1 for where these fit alongside the routine's API trigger and the SMTP credentials.
