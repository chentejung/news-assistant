from news_assistant.fetch import RawItem, fetch_candidates


def test_fetch_candidates_tags_item_matching_a_topic():
    def fake_adapter():
        return [
            RawItem(
                id="1",
                title="New Python web framework simplifies API development",
                url="https://example.com/py313",
                source="Fake",
                points=10,
            )
        ]

    candidates = fetch_candidates([fake_adapter])

    assert len(candidates) == 1
    assert candidates[0].title == "New Python web framework simplifies API development"
    assert candidates[0].candidate_topics == ["Python"]


def test_fetch_candidates_drops_item_matching_no_topic():
    def fake_adapter():
        return [
            RawItem(
                id="2",
                title="Local bakery wins award for best sourdough",
                url="https://example.com/bakery",
                source="Fake",
                points=3,
            )
        ]

    candidates = fetch_candidates([fake_adapter])

    assert candidates == []


def test_fetch_candidates_aggregates_across_multiple_adapters():
    def adapter_one():
        return [
            RawItem(
                id="3",
                title="Kubernetes adds new scheduling feature",
                url="https://example.com/k8s",
                source="Fake A",
                points=20,
            )
        ]

    def adapter_two():
        return [
            RawItem(
                id="4",
                title="New SRE postmortem tool released",
                url="https://example.com/sre-tool",
                source="Fake B",
                points=15,
            )
        ]

    candidates = fetch_candidates([adapter_one, adapter_two])

    assert {c.id for c in candidates} == {"3", "4"}


def test_fetch_candidates_tags_multiple_topics_when_several_match():
    def fake_adapter():
        return [
            RawItem(
                id="5",
                title="Kubernetes outage triggers SRE postmortem",
                url="https://example.com/incident",
                source="Fake",
                points=8,
            )
        ]

    candidates = fetch_candidates([fake_adapter])

    assert len(candidates) == 1
    assert set(candidates[0].candidate_topics) == {"DevOps", "SRE"}
