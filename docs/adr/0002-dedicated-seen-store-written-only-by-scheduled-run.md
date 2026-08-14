# Dedicated seen-store file, written only by the Scheduled Run

Digests are committed to git, so we could have derived Still Trending status by re-parsing prior Digest files instead of maintaining separate state. We chose a dedicated Seen Record store (a small state file, committed alongside the Digest) instead, because tying dedup logic to the human-readable Digest format would make it brittle — a formatting change would silently break repeat-detection.

We also decided On-Demand Runs never write to this store; only the Scheduled Run does. The alternative (any run updates it) would let a casual ad-hoc check change what tomorrow's Scheduled Run considers Still Trending — a surprising side effect for something meant to be exploratory and read-only.
