# Topic classification: keyword pre-filter, then LLM final classification

Trend Items must be matched to one of the fixed Topics before appearing in the Digest. We considered pure deterministic keyword matching (fast, cheap, fully repeatable, but too rigid for a topic like "IT Industry trends") and pure LLM semantic classification of every raw fetched item (flexible, but wasteful to run on everything fetched daily). We chose a hybrid: the fetch script does a fast, wide-recall keyword pre-filter to cut volume, then the Claude Code scheduled agent does final Topic assignment on that reduced set during summarization.

This keeps classification quality high without sending every raw item through an LLM call, at the cost of the pipeline now having two classification stages instead of one to reason about.
