---
name: tech-trends-digest
description: Generate the daily Tech Trend Assistant Digest — fetches candidate Trend Items, classifies and summarizes them by Topic, renders the Digest, and commits it to git. Use when triggered by the scheduled daily run, or when asked to generate today's tech trends digest.
---

# Tech Trends Digest

Produces one day's Digest for the Tech Trend Assistant. See `CONTEXT.md` at the repo root for the vocabulary used below (Topic, Trend Item, Digest, Scheduled Run) and `docs/adr/0001`–`0004` for the architecture this skill implements.

## Steps

1. **Bootstrap the environment if needed.** If `.venv` doesn't exist at the repo root, create it and install the project:
   ```
   python3 -m venv .venv
   .venv/bin/pip install -e .
   ```

2. **Fetch pre-filtered candidates.** Run:
   ```
   .venv/bin/python -m news_assistant.cli
   ```
   This prints a JSON list of candidate Trend Items, each already keyword-pre-filtered against the fixed Topic list and tagged with every Topic its keywords matched (`candidate_topics`). This is broad-recall pre-filtering, not the final classification — some candidates will list more than one Topic, and some keyword matches will be wrong (e.g. a title matching "startup" as in "faster startup" rather than a business startup).

3. **Classify.** For each candidate, decide the single best-fitting Topic from the fixed six (AI/LLMs, DevOps, IT Industry trends, SRE, Systems, Python) using your own judgment, not just `candidate_topics`. Drop any candidate that doesn't genuinely belong to one of the six Topics, even if the keyword pre-filter flagged it.

4. **Summarize.** Write a 1–2 sentence summary of each retained candidate, suitable for a busy reader deciding whether to click through.

5. **Rank and cap.** Within each Topic, rank items by significance (`points` is a signal, weigh it against your own judgment of newsworthiness) and keep only the top 5.

6. **Render the Digest.** Produce a Markdown document with:
   - A top-level heading with today's date
   - One section per Topic that has at least one surviving item, each item as a bullet: the linked title, followed by its summary
   - Topics with zero items after classification are omitted entirely — don't render an empty section

7. **Write and commit.** Save the file to `digests/<YYYY-MM-DD>.md` (create the `digests/` directory if it doesn't exist) and commit it to git with a message like `Add digest for <YYYY-MM-DD>`.

## Out of scope for this skill

These are separate, not-yet-implemented tickets — don't invent them here:

- RSS and GitHub Trending sources, and the Trending Repos section
- Seen Record dedup / "Still Trending" flagging — no seen-store exists yet
- Source failure handling — the fetch script currently has exactly one source; if it fails, let the run fail loudly rather than papering over it
- The push notification on Digest-ready
- On-Demand Runs with ad-hoc Topic overrides — this skill always uses the fixed Topic list
