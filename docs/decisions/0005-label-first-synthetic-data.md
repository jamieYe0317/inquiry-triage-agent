# ADR 0005: Label-first synthetic data

Status: accepted, 2026-11-07

## Context

The project uses synthetic data only. 560 inquiries are too many to write and label by hand, and labels that a model adds after it writes the text tend to agree with that model.

## Decision

1. A scenario catalog fixes the labels (type, segment, safety, expected documents).
2. A seeded script draws 560 specs: 280 DTC and 280 B2B, with persona, tone, length, and a hard-case tag on about 30% of rows.
3. Claude subagents write one message per spec. They see the situation, not the label names.
4. `scripts/build_golden.py` checks the result: no label words, no real brands, example.com emails only, no near-duplicates, and every document ID exists.
5. A second agent labels a random sample blind from `LABELING.md`. The README reports the agreement.

## Consequences

- The label distribution is controlled and reproducible (seed 20261107).
- The text comes from one model family. The router is from the same family, which may make the task easier than real inquiries. The README lists this limit.
- Half of the business senders leave the company field empty, so the router must read the segment from the text.
