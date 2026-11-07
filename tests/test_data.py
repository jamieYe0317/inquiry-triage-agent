"""Checks on the synthetic data: size, balance, label consistency, and the document set."""

import json
from collections import Counter
from pathlib import Path

import pytest

from triage.catalog import DOC_IDS, DOC_INDEX
from triage.handoff import decide
from triage.retrieval import DOCS_DIR, parse_doc
from triage.schemas import InquiryType, Segment

GOLDEN = Path(__file__).resolve().parents[1] / "data" / "eval" / "golden.jsonl"


@pytest.fixture(scope="module")
def rows():
    return [json.loads(line) for line in GOLDEN.open()]


def test_size_and_segments(rows):
    assert len(rows) >= 500
    seg = Counter(r["segment"] for r in rows)
    assert seg["dtc"] >= 250 and seg["b2b"] >= 250


def test_ids_unique_and_split_balanced(rows):
    assert len({r["id"] for r in rows}) == len(rows)
    split = Counter(r["split"] for r in rows)
    assert abs(split["dev"] - split["test"]) <= 7


def test_every_segment_type_pair_is_in_both_splits(rows):
    pairs = Counter((r["segment"], r["type"], r["split"]) for r in rows)
    for seg, typ in {(r["segment"], r["type"]) for r in rows}:
        assert pairs[(seg, typ, "dev")] >= 10 and pairs[(seg, typ, "test")] >= 10


def test_handoff_labels_follow_the_rulebook(rows):
    for r in rows:
        h = decide(InquiryType(r["type"]), Segment(r["segment"]), r["safety"])
        assert (r["team"], r["priority"]) == (h.team.value, h.priority.value), r["id"]
        assert r["cc"] == [t.value for t in h.cc], r["id"]


def test_expected_docs_exist(rows):
    for r in rows:
        for d in r["expected_docs"]:
            assert d in DOC_IDS, (r["id"], d)


def test_hard_case_tags_present(rows):
    tags = Counter(t for r in rows for t in r["tags"])
    for t in ("injection", "spanish", "mixed_intent", "hidden_safety", "typos", "very_short"):
        assert tags[t] >= 10, t


def test_docs_match_the_index():
    files = {p.stem: parse_doc(p) for p in DOCS_DIR.glob("*.md")}
    assert set(files) == set(DOC_IDS)
    for d in DOC_INDEX:
        doc = files[d["id"]]
        assert doc.source_type == d["source_type"] and doc.title == d["title"]
        assert len(doc.sections) >= 3
