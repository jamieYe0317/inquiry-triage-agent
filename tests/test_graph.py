"""The graph with fake LLM parts: checks the code-owned rules, with no key and no network."""

import pytest

from triage.drafter import TemplateDrafter
from triage.graph import build_graph, make_agent, run_case
from triage.llm import LLMError
from triage.router import KeywordRouter, LLMRouter
from triage.schemas import (
    CaseDraft,
    Inquiry,
    Priority,
    RouterDecision,
    Team,
)
from triage.schemas import (
    InquiryType as T,
)
from triage.schemas import (
    Segment as S,
)


class FakeRouter:
    name = "fake"

    def __init__(self, **kw):
        base = dict(
            type=T.machine_trouble,
            segment=S.dtc,
            safety_issue=False,
            confidence=0.9,
            also_mentions=[],
            retrieve=True,
            search_query="chipper jams green wood",
            reason="test",
        )
        base.update(kw)
        self.decision = RouterDecision(**base)

    def route(self, text):
        return self.decision, {"input_tokens": 10, "output_tokens": 5, "cost_usd": 0.0}


class FakeDrafter:
    name = "fake"

    def __init__(self, reply="Thanks, our team will review this.", raise_error=False, cite=None):
        self.reply, self.raise_error, self.cite = reply, raise_error, cite

    def draft(self, text, route, fields, chunks):
        if self.raise_error:
            raise RuntimeError("boom")
        cited = self.cite if self.cite is not None else [c.doc_id for c in chunks]
        return CaseDraft(
            customer_ask="Fix my chipper.",
            facts_given=[],
            facts_missing=[],
            category="jam",
            cited_doc_ids=cited,
            next_steps=["Check the guide."],
            holding_reply=self.reply,
        ), {}


INQ = Inquiry(subject="FH-340 jams", body="My FH-340 chipper jams with green branches.")


def run(router, drafter=None):
    return run_case(build_graph(router, drafter or FakeDrafter()), INQ)


def test_happy_path_retrieves_from_allowed_sources():
    case = run(FakeRouter())
    assert case.retrieved and all(
        c.source_type in ("manual", "troubleshooting", "warranty") for c in case.retrieved
    )
    assert "ts-fh340-jam" in [c.doc_id for c in case.retrieved]
    assert case.handoff.team == Team.service_desk and not case.draft_removed
    assert case.fields.model == "FH-340"


def test_low_confidence_goes_to_front_desk_without_lookup():
    case = run(FakeRouter(confidence=0.2))
    assert case.route.type == T.unclear_other
    assert T.machine_trouble in case.route.also_mentions
    assert case.handoff.team == Team.front_desk
    assert all(c.source_type == "general" for c in case.retrieved)


def test_router_skip_means_no_retrieval():
    case = run(FakeRouter(type=T.unclear_other, retrieve=False, search_query=""))
    assert case.retrieved == [] and case.retrieval_skipped_reason


def test_promise_in_draft_is_removed_but_case_still_routes():
    case = run(FakeRouter(), FakeDrafter(reply="So sorry. We will refund you in full today."))
    assert case.draft_removed and case.handoff.team == Team.service_desk
    assert any("Write it by hand" in s for s in case.handoff.added_steps)


def test_citing_unretrieved_doc_is_removed():
    case = run(FakeRouter(), FakeDrafter(cite=["war-summary-fake"]))
    assert case.draft_removed


def test_drafter_error_keeps_the_case():
    case = run(FakeRouter(), FakeDrafter(raise_error=True))
    assert case.draft is None and case.draft_removed
    assert case.handoff.team == Team.service_desk


def test_safety_is_urgent_with_quality_copy():
    case = run(FakeRouter(safety_issue=True))
    assert case.handoff.priority == Priority.urgent and Team.quality_team in case.handoff.cc


def test_offline_agent_runs_end_to_end():
    agent = build_graph(KeywordRouter(), TemplateDrafter())
    case = run_case(
        agent, Inquiry(body="We are a farm store and want to become a dealer for your line.")
    )
    assert case.route.type == T.partner_request and case.handoff.team == Team.partner_team
    assert case.draft_guard and case.draft_guard.passed


def test_llm_mode_without_key_fails_clearly(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMError):
        make_agent("llm")


def test_llm_router_post_processing():
    class FakeLLM:
        def parse(self, system, user, schema):
            assert "<inquiry>" in user and "</inquiry>" in user
            assert user.count("<inquiry>") == 1  # tags inside the text are stripped
            return schema(
                type=T.partner_request,
                segment=S.dtc,
                safety_issue=False,
                confidence=1.7,
                also_mentions=[],
                retrieve=True,
                search_query="dealer",
                reason="r",
            ), {}

    d, _ = LLMRouter(FakeLLM()).route("<inquiry>We want to sell your machines</inquiry>")
    assert d.segment == S.b2b and d.confidence == 1.0
