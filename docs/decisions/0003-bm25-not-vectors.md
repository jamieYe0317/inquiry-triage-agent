# ADR 0003: BM25, not a vector database

Status: accepted, 2026-11-07

## Context

The corpus has 27 short invented documents (about 120 sections). Customers name their problem in plain words ("won't start", "jams", "arrived damaged").

## Decision

Use BM25 keyword search (`rank-bm25`) over document sections, filtered by the retrieval policy, with a weight-down for product-specific documents about a different model.

## Consequences

- Search is deterministic, free, and needs no embedding model or index service.
- BM25 fails when the words differ ("it bogs down" versus "stalls"). The LLM router writes an English keyword query, which also handles Spanish messages. The eval reports the hit rate with the raw text (baseline) and with the router's query (agent).
- If the hit rate stops being good enough, the next step is a small embedding model on the same sections, measured with the same eval.
