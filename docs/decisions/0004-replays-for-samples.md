# ADR 0004: Saved runs for the demo's sample buttons

Status: accepted, 2026-11-07

## Context

The public demo has a $5 monthly LLM limit. A visitor who clicks every sample should not use it up.

## Decision

The sample buttons show saved runs from `data/replays/`, made by `scripts/make_replays.py`. Only the "Write your own" tab calls the LLM, with a limit of 10 runs per visitor and 100 runs per day. When the key is missing or the limit is reached, that tab runs the free no-LLM baseline and says so.

## Consequences

- The samples cost nothing and always work.
- Saved runs can go stale when the prompts change. Each saved file records its date and mode, and the app shows them.
