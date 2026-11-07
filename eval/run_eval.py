"""Run the triage agent on the golden set and score it.

Examples:
  uv run python eval/run_eval.py --mode offline --split test          # no key, no cost
  uv run python eval/run_eval.py --mode llm --split dev --limit 40    # needs ANTHROPIC_API_KEY
  uv run python eval/run_eval.py --mode llm --split test --runs 3

Writes eval/results/<date>_<mode>_<split>.json and .md.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from triage.graph import make_agent, run_case  # noqa: E402
from triage.schemas import Inquiry  # noqa: E402

GOLDEN = ROOT / "data" / "eval" / "golden.jsonl"
RESULTS = ROOT / "eval" / "results"
TYPES = ["machine_trouble", "quality_complaint", "partner_request", "unclear_other"]
PROMISE_KINDS = (
    "promise_",
    "claims_approval",
    "guarantee",
    "price_or_discount",
    "partner_terms",
    "decides_remedy",
)


def load_rows(split: str, limit: int | None, ids: list[str] | None) -> list[dict]:
    rows = [json.loads(line) for line in GOLDEN.open()]
    if split != "all":
        rows = [r for r in rows if r["split"] == split]
    if ids:
        rows = [r for r in rows if r["id"] in ids]
    if limit:
        # take a spread across types, not just the first rows
        rows = sorted(rows, key=lambda r: (hash(r["id"]) % 997, r["id"]))[:limit]
    return rows


def predict(agent, row: dict) -> dict:
    inq = Inquiry(
        id=row["id"],
        subject=row["subject"],
        body=row["body"],
        sender_name=row["sender_name"],
        sender_org=row["sender_org"],
    )
    t0 = time.perf_counter()
    try:
        case = run_case(agent, inq)
    except Exception as e:  # record the failure and keep going
        return {
            "id": row["id"],
            "error": f"{type(e).__name__}: {e}",
            "seconds": time.perf_counter() - t0,
        }
    violations = case.draft_guard.violations if case.draft_guard else []
    usage = case.usage or {}
    return {
        "id": row["id"],
        "type": case.route.type.value,
        "segment": case.route.segment.value,
        "safety": case.route.safety_issue,
        "confidence": case.route.confidence,
        "retrieved": [c.doc_id for c in case.retrieved],
        "team": case.handoff.team.value,
        "cc": [t.value for t in case.handoff.cc],
        "priority": case.handoff.priority.value,
        "draft_removed": case.draft_removed,
        "violations": violations,
        "input_flags": case.input_flags,
        "input_tokens": sum(u.get("input_tokens", 0) for u in usage.values()),
        "output_tokens": sum(u.get("output_tokens", 0) for u in usage.values()),
        "cost_usd": sum(u.get("cost_usd", 0.0) for u in usage.values()),
        "seconds": round(time.perf_counter() - t0, 3),
    }


def pct(n: int, d: int) -> float | None:
    return round(100 * n / d, 1) if d else None


def score(rows: list[dict], preds: dict[str, dict]) -> dict:
    ok = [r for r in rows if "error" not in preds[r["id"]]]
    P = lambda r: preds[r["id"]]  # noqa: E731
    m: dict = {"rows": len(rows), "errors": len(rows) - len(ok)}
    m["type_accuracy"] = pct(sum(P(r)["type"] == r["type"] for r in ok), len(rows))
    f1s = []
    for t in TYPES:
        tp = sum(P(r)["type"] == t and r["type"] == t for r in ok)
        fp = sum(P(r)["type"] == t and r["type"] != t for r in ok)
        fn = sum(P(r)["type"] != t and r["type"] == t for r in rows if r in ok) + sum(
            1 for r in rows if r not in ok and r["type"] == t
        )
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    m["type_macro_f1"] = round(100 * statistics.mean(f1s), 1)
    m["segment_accuracy"] = pct(sum(P(r)["segment"] == r["segment"] for r in ok), len(rows))
    need = [r for r in rows if r["expected_docs"]]
    m["retrieval_hit_at_3"] = pct(
        sum(r in ok and bool(set(P(r)["retrieved"]) & set(r["expected_docs"])) for r in need),
        len(need),
    )
    need_ok = [r for r in need if r in ok and P(r)["type"] == r["type"]]
    m["retrieval_hit_at_3_when_type_correct"] = pct(
        sum(bool(set(P(r)["retrieved"]) & set(r["expected_docs"])) for r in need_ok), len(need_ok)
    )
    noneed = [r for r in rows if not r["expected_docs"]]
    m["retrieval_skip_accuracy"] = pct(
        sum(r in ok and not P(r)["retrieved"] for r in noneed), len(noneed)
    )
    m["team_accuracy"] = pct(sum(P(r)["team"] == r["team"] for r in ok), len(rows))
    m["priority_accuracy"] = pct(sum(P(r)["priority"] == r["priority"] for r in ok), len(rows))
    m["handoff_accuracy"] = pct(
        sum(P(r)["team"] == r["team"] and P(r)["priority"] == r["priority"] for r in ok), len(rows)
    )
    safe = [r for r in rows if r["safety"]]
    m["safety_recall"] = pct(sum(r in ok and P(r)["priority"] == "urgent" for r in safe), len(safe))
    flagged = [r for r in ok if P(r)["priority"] == "urgent"]
    m["safety_precision"] = pct(sum(r["safety"] for r in flagged), len(flagged))
    m["drafts_with_promise_language"] = sum(
        any(v.startswith(PROMISE_KINDS) for v in P(r)["violations"]) for r in ok
    )
    m["drafts_removed_by_guard"] = sum(P(r)["draft_removed"] for r in ok)
    m["shipped_drafts_with_violations"] = sum(
        (not P(r)["draft_removed"]) and bool(P(r)["violations"]) for r in ok
    )
    inj = [r for r in rows if "injection" in r["tags"]]
    m["injection_rows_handled"] = (
        f"{sum(r in ok and P(r)['type'] == r['type'] and P(r)['team'] == r['team'] for r in inj)}/{len(inj)}"
    )
    m["cost_usd_per_inquiry"] = (
        round(statistics.mean(P(r)["cost_usd"] for r in ok), 6) if ok else None
    )
    m["tokens_per_inquiry"] = (
        round(statistics.mean(P(r)["input_tokens"] + P(r)["output_tokens"] for r in ok))
        if ok
        else None
    )
    secs = sorted(P(r)["seconds"] for r in ok)
    m["seconds_median"] = round(statistics.median(secs), 2) if secs else None
    m["seconds_p95"] = round(secs[int(0.95 * (len(secs) - 1))], 2) if secs else None
    return m


def breakdown(rows: list[dict], preds: dict[str, dict]) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[f"segment={r['segment']}"].append(r)
        groups[f"type={r['type']}"].append(r)
        for t in r["tags"] or ["none"]:
            groups[f"tag={t}"].append(r)
    out = {}
    for g, rs in sorted(groups.items()):
        ok = [r for r in rs if "error" not in preds[r["id"]]]
        out[g] = {
            "n": len(rs),
            "type_accuracy": pct(sum(preds[r["id"]]["type"] == r["type"] for r in ok), len(rs)),
            "handoff_accuracy": pct(
                sum(
                    preds[r["id"]]["team"] == r["team"]
                    and preds[r["id"]]["priority"] == r["priority"]
                    for r in ok
                ),
                len(rs),
            ),
        }
    return out


def confusion(rows: list[dict], preds: dict[str, dict]) -> dict:
    c = Counter((r["type"], preds[r["id"]].get("type", "error")) for r in rows)
    return {t: {p: c[(t, p)] for p in [*TYPES, "error"] if c[(t, p)]} for t in TYPES}


def failures(rows: list[dict], preds: dict[str, dict]) -> list[dict]:
    out = []
    for r in rows:
        p = preds[r["id"]]
        if "error" in p:
            out.append({"id": r["id"], "problem": p["error"]})
            continue
        probs = []
        if p["type"] != r["type"]:
            probs.append(f"type {r['type']} -> {p['type']}")
        if p["segment"] != r["segment"]:
            probs.append(f"segment {r['segment']} -> {p['segment']}")
        if p["team"] != r["team"] or p["priority"] != r["priority"]:
            probs.append(f"handoff {r['team']}/{r['priority']} -> {p['team']}/{p['priority']}")
        if r["expected_docs"] and not set(p["retrieved"]) & set(r["expected_docs"]):
            probs.append(f"docs {r['expected_docs']} not in {p['retrieved']}")
        if not r["expected_docs"] and p["retrieved"]:
            probs.append(f"retrieved {p['retrieved']} but none needed")
        if probs:
            out.append(
                {
                    "id": r["id"],
                    "tags": r["tags"],
                    "problem": "; ".join(probs),
                    "text": (r["subject"] + " | " + r["body"])[:160],
                }
            )
    return out


def to_markdown(meta: dict, summary: dict, bd: dict, conf: dict, fails: list[dict]) -> str:
    lines = [
        f"# Eval: {meta['mode']} on {meta['split']} ({meta['rows']} rows, {meta['runs']} run(s))",
        "",
        f"Date: {meta['date']}. Model: {meta['model']}. Golden set: data/eval/golden.jsonl.",
        "",
        "| Metric | Mean | Lowest run |",
        "|---|---:|---:|",
    ]
    for k, v in summary["mean"].items():
        lines.append(f"| {k} | {v} | {summary['min'].get(k, '')} |")
    lines += [
        "",
        "## Confusion matrix (rows = label, columns = prediction), run 1",
        "",
        "| label \\ predicted | " + " | ".join(TYPES) + " | error |",
        "|---|" + "---:|" * (len(TYPES) + 1),
    ]
    for t in TYPES:
        lines.append(
            f"| {t} | " + " | ".join(str(conf[t].get(p, 0)) for p in [*TYPES, "error"]) + " |"
        )
    lines += [
        "",
        "## Breakdown, run 1",
        "",
        "| Group | n | Type accuracy | Hand-off accuracy |",
        "|---|---:|---:|---:|",
    ]
    for g, v in bd.items():
        lines.append(f"| {g} | {v['n']} | {v['type_accuracy']} | {v['handoff_accuracy']} |")
    lines += [
        "",
        f"## Failures, run 1 ({len(fails)} rows; first 60 shown, all in the JSON file)",
        "",
    ]
    for f in fails[:60]:
        lines.append(f"- `{f['id']}` {f.get('tags', '')} {f['problem']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["offline", "llm"], default="offline")
    ap.add_argument("--split", choices=["dev", "test", "all"], default="dev")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--tag", default="", help="extra label for the output file name")
    a = ap.parse_args()

    rows = load_rows(a.split, a.limit, a.ids)
    agent = make_agent(a.mode)
    workers = a.workers or (8 if a.mode == "llm" else 1)
    from triage.llm import DEFAULT_MODEL

    model = DEFAULT_MODEL if a.mode == "llm" else "none (keyword router + template drafter)"

    runs = []
    for i in range(a.runs):
        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as ex:
            preds = {p["id"]: p for p in ex.map(lambda r: predict(agent, r), rows)}
        m = score(rows, preds)
        runs.append((m, preds))
        print(
            f"run {i + 1}/{a.runs} done in {time.perf_counter() - t0:.0f}s: "
            f"type {m['type_accuracy']}%, hand-off {m['handoff_accuracy']}%, "
            f"docs {m['retrieval_hit_at_3']}%, errors {m['errors']}"
        )

    numeric = [k for k, v in runs[0][0].items() if isinstance(v, (int, float))]
    worse_is_higher = {
        "errors",
        "drafts_with_promise_language",
        "drafts_removed_by_guard",
        "shipped_drafts_with_violations",
        "cost_usd_per_inquiry",
        "tokens_per_inquiry",
        "seconds_median",
        "seconds_p95",
    }
    summary = {"mean": {}, "min": {}}
    for k, v in runs[0][0].items():
        if k in numeric and all(r[0][k] is not None for r in runs):
            vals = [r[0][k] for r in runs]
            summary["mean"][k] = round(statistics.mean(vals), 6 if "usd" in k else 1)
            summary["min"][k] = max(vals) if k in worse_is_higher else min(vals)
        else:
            summary["mean"][k] = v
    first_preds = runs[0][1]
    meta = {
        "date": date.today().isoformat(),
        "mode": a.mode,
        "split": a.split,
        "rows": len(rows),
        "runs": a.runs,
        "model": model,
        "limit": a.limit,
    }
    bd, conf, fails = (
        breakdown(rows, first_preds),
        confusion(rows, first_preds),
        failures(rows, first_preds),
    )
    RESULTS.mkdir(parents=True, exist_ok=True)
    stem = (
        f"{meta['date']}_{a.mode}_{a.split}"
        + (f"_n{a.limit}" if a.limit else "")
        + (f"_{a.tag}" if a.tag else "")
    )
    (RESULTS / f"{stem}.json").write_text(
        json.dumps(
            {
                "meta": meta,
                "summary": summary,
                "runs": [r[0] for r in runs],
                "breakdown": bd,
                "confusion": conf,
                "failures": fails,
                "predictions_run1": list(first_preds.values()),
            },
            indent=1,
        )
    )
    (RESULTS / f"{stem}.md").write_text(to_markdown(meta, summary, bd, conf, fails))
    print(json.dumps(summary["mean"], indent=1))
    print(f"wrote {RESULTS / stem}.json and .md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
