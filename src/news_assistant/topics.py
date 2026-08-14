"""The fixed set of Topics this project tracks, and the keywords used to
pre-filter candidate items against them (broad recall, per ADR-0004 —
final single-Topic assignment happens later, outside this module)."""

import re

TOPICS: dict[str, list[str]] = {
    "AI/LLMs": [
        "ai",
        "artificial intelligence",
        "llm",
        "large language model",
        "gpt",
        "openai",
        "anthropic",
        "claude",
        "gemini",
        "machine learning",
        "neural network",
        "chatbot",
        "genai",
        "transformer model",
    ],
    "DevOps": [
        "devops",
        "ci/cd",
        "continuous integration",
        "continuous deployment",
        "kubernetes",
        "k8s",
        "docker",
        "container",
        "terraform",
        "infrastructure as code",
        "helm",
        "ansible",
    ],
    "IT Industry trends": [
        "layoffs",
        "funding round",
        "acquisition",
        "ipo",
        "startup",
        "venture capital",
        "merger",
        "valuation",
        "tech industry",
        "big tech",
    ],
    "SRE": [
        "sre",
        "site reliability",
        "postmortem",
        "reliability engineering",
        "observability",
        "outage",
        "on-call",
        "incident response",
        "slo",
        "sla",
    ],
    "Systems": [
        "operating system",
        "kernel",
        "linux",
        "distributed systems",
        "database engine",
        "compiler",
        "systems programming",
        "concurrency",
        "low-level",
    ],
    "Python": [
        "python",
        "pypi",
        "django",
        "flask",
        "fastapi",
        "pandas",
        "numpy",
    ],
}


def match_topics(title: str) -> list[str]:
    """Return every Topic whose keywords appear in `title` as whole words
    (case-insensitive). Word boundaries matter: a short keyword like "ai"
    must not match inside "container" or "explain"."""
    lowered = title.lower()
    return [
        topic
        for topic, keywords in TOPICS.items()
        if any(re.search(rf"\b{re.escape(keyword)}\b", lowered) for keyword in keywords)
    ]
