# ADR 0001: A fixed graph, not a free agent loop

Status: accepted, 2026-11-07

## Context

Triage has a known set of steps: read, sort, look up, summarize, hand off. A free agent loop lets the model choose its own tools and its own number of turns.

## Decision

Use a fixed LangGraph graph: `guard_in → route → (retrieve | skip) → draft → guard_out → handoff`. The LLM makes 2 decisions: the route and the draft. One conditional edge decides whether to retrieve.

## Consequences

- Each run makes exactly 2 LLM calls, so the cost and the time per inquiry are predictable.
- Each node has a unit test with a fake LLM (`tests/test_graph.py`).
- The agent cannot do things outside the graph, such as ask the sender a follow-up question. A person does that.
