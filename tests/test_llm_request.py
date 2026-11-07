"""Contract test for the LLM path, against a mock HTTP server. No key and no network.

It checks the request that the SDK sends (model, effort, JSON schema) and that the
response parses into our Pydantic models, with cost accounting.
"""

import json

import anthropic
import httpx2
import pytest

from triage.drafter import LLMDrafter
from triage.llm import LLM, LLMError
from triage.router import LLMRouter
from triage.schemas import ExtractedFields, InquiryType, RouterDecision, Segment

ROUTE = {
    "type": "machine_trouble",
    "segment": "dtc",
    "safety_issue": False,
    "confidence": 0.9,
    "also_mentions": [],
    "retrieve": True,
    "search_query": "FH-340 jams green wood",
    "reason": "r",
}
DRAFT = {
    "customer_ask": "Fix a jam.",
    "facts_given": ["FH-340"],
    "facts_missing": ["serial"],
    "category": "jam",
    "cited_doc_ids": [],
    "next_steps": ["Check the guide."],
    "holding_reply": "Thanks, our team will review this.",
}


def fake_llm(monkeypatch, payload, stop_reason="end_turn"):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-not-real")
    seen = {}

    def handler(req):
        body = json.loads(req.content)
        seen.update(body)
        return httpx2.Response(
            200,
            json={
                "id": "msg_1",
                "type": "message",
                "role": "assistant",
                "model": body["model"],
                "content": [{"type": "text", "text": json.dumps(payload)}],
                "stop_reason": stop_reason,
                "stop_sequence": None,
                "usage": {"input_tokens": 1000, "output_tokens": 200},
            },
        )

    llm = LLM()
    llm.client = anthropic.Anthropic(
        api_key="test-not-real", http_client=httpx2.Client(transport=httpx2.MockTransport(handler))
    )
    return llm, seen


def test_router_request_and_parse(monkeypatch):
    llm, seen = fake_llm(monkeypatch, ROUTE)
    decision, usage = LLMRouter(llm).route("My FH-340 jams")
    assert decision.type == InquiryType.machine_trouble
    assert seen["model"] == "claude-haiku-5-5"
    assert seen["output_config"]["effort"] == "low"
    assert seen["output_config"]["format"]["type"] == "json_schema"
    assert "<inquiry>" in seen["messages"][0]["content"]
    assert usage["cost_usd"] == pytest.approx((1000 * 0.10 + 200 * 0.50) / 1e6)


def test_drafter_request_includes_docs(monkeypatch):
    llm, seen = fake_llm(monkeypatch, DRAFT)
    route = RouterDecision(**{**ROUTE, "type": InquiryType.machine_trouble, "segment": Segment.dtc})
    draft, _ = LLMDrafter(llm).draft("My FH-340 jams", route, ExtractedFields(model="FH-340"), [])
    assert draft.customer_ask == "Fix a jam."
    assert "<docs>" in seen["messages"][0]["content"]


def test_refusal_raises(monkeypatch):
    llm, _ = fake_llm(monkeypatch, ROUTE, stop_reason="refusal")
    with pytest.raises(LLMError):
        LLMRouter(llm).route("text")
