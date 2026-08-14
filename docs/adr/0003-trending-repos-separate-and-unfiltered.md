# Trending Repos are a separate, unfiltered section

Trend Items (Hacker News + RSS) are strictly filtered to the fixed Topic list — items matching none of the six Topics are dropped. We deliberately did not apply the same treatment to Trending Repos: they get their own Digest section and are shown unfiltered (top trending overall), not grouped into Topic buckets.

The reasoning: a Trending Repo signals developer momentum (e.g., stars/day), which is a different kind of trend than a reported news story, and forcing it through the same Topic-match logic as news would either lose most repos to strict filtering or require stretching Topic definitions to fit. Keeping it a distinct, unfiltered section avoids both.
