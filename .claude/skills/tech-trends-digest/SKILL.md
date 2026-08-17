---
name: tech-trends-digest
description: Generate the daily Tech Trend Assistant Digest — reads the day's pre-fetched candidate Trend Items, classifies and summarizes them by Topic, renders the Digest, commits it to git, and emails it. Triggered by the Vercel fetch job's API trigger call; also usable to generate today's digest on demand.
---

# Tech Trends Digest

Produces one day's Digest for the Tech Trend Assistant. See `CONTEXT.md` at the repo root for the vocabulary used below (Topic, Trend Item, Fetch Payload, Digest, Scheduled Run) and `docs/adr/0001`–`0005` for the architecture this skill implements. As of ADR-0005, this routine no longer fetches Hacker News itself — a Vercel Function does that on a daily schedule and calls this routine's API trigger with the result.

## Steps

1. **Bootstrap the environment if needed.** If `.venv` doesn't exist at the repo root, create it and install the project:
   ```
   python3 -m venv .venv
   .venv/bin/pip install -e .
   ```

2. **Read the incoming trigger payload.** The API trigger that started this run carries `{"status": "success"}` or `{"status": "failure", "error": "..."}`.

   - **On failure:** send the failure-notice email and stop — do not write or commit anything, since a failed fetch has no candidates and nothing fits the Digest definition:
     ```
     echo "<the error text>" | .venv/bin/python -m news_assistant.notify_cli --subject "Tech Trends Digest: fetch failed for <YYYY-MM-DD>"
     ```
   - **On success:** continue to step 3.

3. **Read the Fetch Payload.** Using the Google Drive MCP connector, read the single well-known Fetch Payload file Vercel just wrote. It's a JSON list of candidate Trend Items, each already keyword-pre-filtered against the fixed Topic list and tagged with every Topic its keywords matched (`candidate_topics`). This is broad-recall pre-filtering, not the final classification — some candidates will list more than one Topic, and some keyword matches will be wrong (e.g. a title matching "startup" as in "faster startup" rather than a business startup).

4. **Classify.** For each candidate, decide the single best-fitting Topic from the fixed six (AI/LLMs, DevOps, IT Industry trends, SRE, Systems, Python) using your own judgment, not just `candidate_topics`. Drop any candidate that doesn't genuinely belong to one of the six Topics, even if the keyword pre-filter flagged it.

5. **Summarize.** Write a 1–2 sentence summary of each retained candidate, suitable for a busy reader deciding whether to click through.

6. **Rank and cap.** Within each Topic, rank items by significance (`points` is a signal, weigh it against your own judgment of newsworthiness) and keep only the top 5.

7. **Render the Digest.** Produce a Markdown document with:
   - A top-level heading with today's date
   - One section per Topic that has at least one surviving item, each item as a bullet: the linked title, followed by its summary
   - Topics with zero items after classification are omitted entirely — don't render an empty section

   Save the file to `digests/<YYYY-MM-DD>.md` (create the `digests/` directory if it doesn't exist) and commit it to git with a message like `Add digest for <YYYY-MM-DD>`.

8. **Email the rendered Digest** (SMTP + Gmail App Password, per ADR-0005):
   ```
   cat digests/<YYYY-MM-DD>.md | .venv/bin/python -m news_assistant.notify_cli --subject "Tech Trends Digest: <YYYY-MM-DD>"
   ```
   (The failure case's email is sent directly from step 2 and never reaches this step.)

Both email steps require `SMTP_USERNAME`, `SMTP_APP_PASSWORD`, and `DIGEST_TO` set in the routine's environment (`SMTP_HOST`/`SMTP_PORT` default to `smtp.gmail.com`/`587`).

## Out of scope for this skill

These are separate, not-yet-implemented tickets — don't invent them here:

- RSS and GitHub Trending sources, and the Trending Repos section (#3)
- Seen Record dedup / "Still Trending" flagging — no seen-store exists yet (#5)
- Multi-source failure resilience / graceful degradation across sources (#6) — this skill's only failure handling is the single Vercel fetch attempt's explicit success/failure status from step 2
- On-Demand Runs with ad-hoc Topic overrides — this skill always uses the fixed Topic list (#7)
