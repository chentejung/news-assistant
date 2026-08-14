# Tech Trend Assistant

Produces a daily, topic-curated digest of tech-industry trends from a fixed set of sources, plus an on-demand mode for ad-hoc queries.

## Language

**Topic**:
One of the fixed subject areas the user tracks (AI/LLMs, DevOps, IT Industry trends, SRE, Systems, Python). A Trend Item must match exactly one Topic to appear in the Digest; items matching none are excluded.
_Avoid_: Category, tag.

**Trend Item**:
A single news story, sourced from Hacker News or an RSS feed, that has been matched to a Topic and summarized for inclusion in a Digest.
_Avoid_: Story, article, headline — those refer to unprocessed source material, not a Trend Item.

**Trending Repo**:
A GitHub repository showing above-normal attention within the tracked period. Shown separately from Trend Items and not filtered by Topic, because repo momentum is a different kind of signal than reported news.
_Avoid_: Repository, project — reserve "Trending Repo" for this specific curated sense.

**Digest**:
The dated output delivered to the user: Trend Items grouped by Topic, plus a Trending Repos section.
_Avoid_: Report, newsletter, summary.

**Still Trending**:
The state of a Trend Item that also appeared in a prior Digest. Shown as a flag on the item rather than removing it from the current Digest.
_Avoid_: Duplicate, repeat — those imply removal, not flagging.

**Seen Record**:
The record of a Trend Item's first appearance, used to determine whether a later appearance should be flagged Still Trending.
_Avoid_: History, cache.

**Scheduled Run**:
The automatic, daily production of a Digest using the fixed Topic list. The only kind of run that writes Seen Records.
_Avoid_: Cron job, batch job.

**On-Demand Run**:
A user-triggered production of a Digest, optionally scoped to Topics outside the fixed list. Never writes Seen Records, so ad-hoc queries can't change what a later Scheduled Run considers Still Trending.
_Avoid_: Manual run, ad-hoc query (fine in conversation, but "On-Demand Run" is the canonical term).
