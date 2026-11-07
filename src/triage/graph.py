"""The fixed triage graph, built with LangGraph.

guard_in -> route -> (retrieve | skip) -> draft -> guard_out -> handoff

The LLM makes two decisions (route, draft). Code makes the rest: the allowed sources,
the low-confidence fallback, the promise check, the team, and the priority.
"""

from __future__ import annotations

import time
from typing import Any, Protocol, TypedDict

from langgraph.graph import END, START, StateGraph

from . import handoff as handoff_rules
from .guards import check_draft, clean_input, extract_fields
from .policy import ALLOWED_SOURCES, LOW_CONFIDENCE
from .retrieval import Retriever, default_retriever
from .schemas import (
    Case,
    CaseDraft,
    ExtractedFields,
    GuardResult,
    Handoff,
    Inquiry,
    InquiryType,
    RetrievedChunk,
    RouterDecision,
)


class Router(Protocol):
    name: str

    def route(self, text: str) -> tuple[RouterDecision, dict]: ...


class Drafter(Protocol):
    name: str

    def draft(
        self,
        text: str,
        route: RouterDecision,
        fields: ExtractedFields,
        chunks: list[RetrievedChunk],
    ) -> tuple[CaseDraft, dict]: ...


class State(TypedDict, total=False):
    inquiry: Inquiry
    text: str
    input_flags: list[str]
    route: RouterDecision
    fields: ExtractedFields
    retrieved: list[RetrievedChunk]
    skip_reason: str | None
    draft: CaseDraft | None
    guard: GuardResult | None
    draft_removed: bool
    handoff: Handoff
    usage: dict[str, Any]
    timings_ms: dict[str, float]


def _timed(name: str, state: State, t0: float) -> dict[str, float]:
    timings = dict(state.get("timings_ms", {}))
    timings[name] = round((time.perf_counter() - t0) * 1000, 1)
    return timings


def _add_usage(state: State, step: str, usage: dict) -> dict[str, Any]:
    total = dict(state.get("usage", {}))
    if usage:
        total[step] = usage
    return total


def build_graph(router: Router, drafter: Drafter, retriever: Retriever | None = None):
    retriever = retriever or default_retriever()

    def guard_in(state: State) -> State:
        t0 = time.perf_counter()
        text, flags = clean_input(state["inquiry"].as_text())
        return {
            "text": text,
            "input_flags": flags,
            "fields": extract_fields(text),
            "timings_ms": _timed("guard_in", state, t0),
        }

    def route(state: State) -> State:
        t0 = time.perf_counter()
        decision, usage = router.route(state["text"])
        if decision.confidence < LOW_CONFIDENCE and decision.type != InquiryType.unclear_other:
            decision = decision.model_copy(
                update={
                    "also_mentions": [decision.type, *decision.also_mentions],
                    "type": InquiryType.unclear_other,
                    "reason": f"Low confidence ({decision.confidence:.2f}); a person should sort it. "
                    + decision.reason,
                }
            )
        return {
            "route": decision,
            "usage": _add_usage(state, "router", usage),
            "timings_ms": _timed("route", state, t0),
        }

    def should_retrieve(state: State) -> str:
        r = state["route"]
        return "retrieve" if r.retrieve and ALLOWED_SOURCES[r.type] else "skip"

    def retrieve(state: State) -> State:
        t0 = time.perf_counter()
        r = state["route"]
        query = r.search_query or state["text"]
        chunks = retriever.search(query, ALLOWED_SOURCES[r.type], model=state["fields"].model)
        return {
            "retrieved": chunks,
            "skip_reason": None,
            "timings_ms": _timed("retrieve", state, t0),
        }

    def skip(state: State) -> State:
        return {"retrieved": [], "skip_reason": "The router found no document that would help."}

    def draft(state: State) -> State:
        t0 = time.perf_counter()
        try:
            d, usage = drafter.draft(
                state["text"], state["route"], state["fields"], state["retrieved"]
            )
        except Exception as e:  # a failed draft must not lose the case
            return {
                "draft": None,
                "draft_removed": True,
                "guard": GuardResult(passed=False, violations=[f"drafter_error: {e}"]),
                "timings_ms": _timed("draft", state, t0),
            }
        return {
            "draft": d,
            "usage": _add_usage(state, "drafter", usage),
            "timings_ms": _timed("draft", state, t0),
        }

    def guard_out(state: State) -> State:
        if state.get("draft") is None:
            return {}
        result = check_draft(state["draft"], [c.doc_id for c in state["retrieved"]])
        return {"guard": result, "draft_removed": not result.passed}

    def do_handoff(state: State) -> State:
        r = state["route"]
        h = handoff_rules.decide(r.type, r.segment, r.safety_issue, state["fields"])
        if state.get("draft_removed"):
            h.added_steps.append(
                "The draft failed the safety check and was removed. Write it by hand."
            )
        return {"handoff": h}

    g = StateGraph(State)
    g.add_node("guard_in", guard_in)
    g.add_node("route", route)
    g.add_node("retrieve", retrieve)
    g.add_node("skip", skip)
    g.add_node("draft", draft)
    g.add_node("guard_out", guard_out)
    g.add_node("handoff", do_handoff)
    g.add_edge(START, "guard_in")
    g.add_edge("guard_in", "route")
    g.add_conditional_edges("route", should_retrieve, {"retrieve": "retrieve", "skip": "skip"})
    g.add_edge("retrieve", "draft")
    g.add_edge("skip", "draft")
    g.add_edge("draft", "guard_out")
    g.add_edge("guard_out", "handoff")
    g.add_edge("handoff", END)
    return g.compile()


def run_case(graph, inquiry: Inquiry) -> Case:
    s: State = graph.invoke({"inquiry": inquiry, "usage": {}, "timings_ms": {}})
    return Case(
        inquiry=inquiry,
        input_flags=s.get("input_flags", []),
        route=s["route"],
        fields=s["fields"],
        retrieval_skipped_reason=s.get("skip_reason"),
        retrieved=s.get("retrieved", []),
        draft=s.get("draft"),
        draft_guard=s.get("guard"),
        draft_removed=bool(s.get("draft_removed")),
        handoff=s["handoff"],
        usage=s.get("usage", {}),
        timings_ms=s.get("timings_ms", {}),
    )


def make_agent(mode: str = "llm"):
    """mode 'llm' = LLM router + LLM drafter. mode 'offline' = keyword router + template drafter."""
    from .drafter import LLMDrafter, TemplateDrafter
    from .router import KeywordRouter, LLMRouter

    if mode == "offline":
        return build_graph(KeywordRouter(), TemplateDrafter())
    from .llm import LLM

    llm = LLM()
    return build_graph(LLMRouter(llm), LLMDrafter(llm))
