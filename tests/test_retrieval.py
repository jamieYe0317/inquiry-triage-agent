import pytest

from triage.policy import ALLOWED_SOURCES
from triage.retrieval import default_retriever, tokenize
from triage.schemas import InquiryType as T


@pytest.fixture(scope="module")
def r():
    return default_retriever()


def test_tokenize_normalizes_model_numbers():
    for s in ("FH-340", "fh 340", "FH340", "fh_340"):
        assert "fh340" in tokenize(f"my {s} jams")


def test_results_respect_allowed_sources(r):
    for itype, allowed in ALLOWED_SOURCES.items():
        for c in r.search(
            "machine will not start, damaged box, become a dealer, shipping", allowed, k=5
        ):
            assert c.source_type in allowed, (itype, c.doc_id)


def test_no_allowed_sources_returns_nothing(r):
    assert r.search("anything", ()) == []


@pytest.mark.parametrize(
    "query,itype,model,expected",
    [
        (
            "chipper keeps jamming with wet green branches",
            T.machine_trouble,
            "FH-340",
            "ts-fh340-jam",
        ),
        (
            "generator starts then shuts off after a few minutes",
            T.machine_trouble,
            "FH-G7",
            "ts-fhg7-nostart",
        ),
        (
            "generator runs but no power at the outlets",
            T.machine_trouble,
            "FH-G7",
            "ts-fhg7-output",
        ),
        (
            "splitter ram slow hydraulic fluid leaking",
            T.machine_trouble,
            "FH-210",
            "ts-fh210-hydraulic",
        ),
        (
            "pressure washer low pressure pulsing spray",
            T.machine_trouble,
            "FH-P90",
            "ts-fhp90-pressure",
        ),
        ("we want to become a dealer and carry your line", T.partner_request, None, "par-apply"),
        ("exclusive territory for our region", T.partner_request, None, "par-territory"),
        ("box arrived crushed and the frame is bent", T.quality_complaint, None, "qa-returns-dtc"),
        ("pallet delivered damaged freight claim", T.quality_complaint, None, "qa-freight-damage"),
        ("where is my order tracking not updated", T.unclear_other, None, "gen-shipping"),
    ],
)
def test_known_queries_hit(r, query, itype, model, expected):
    ids = [c.doc_id for c in r.search(query, ALLOWED_SOURCES[itype], model=model)]
    assert expected in ids, ids


def test_product_filter_prefers_the_right_manual(r):
    ids = [
        c.doc_id
        for c in r.search("oil change interval maintenance schedule", ("manual",), model="FH-520")
    ]
    assert ids[0] == "man-fh520"
