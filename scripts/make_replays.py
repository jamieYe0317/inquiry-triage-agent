"""Save agent runs for the demo's sample buttons (data/replays/*.json).

Sample buttons replay these files, so they cost nothing and work with no key.
  uv run python scripts/make_replays.py --mode offline   # baseline, no key
  uv run python scripts/make_replays.py --mode llm       # the real agent, needs ANTHROPIC_API_KEY
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from triage.graph import make_agent, run_case  # noqa: E402
from triage.schemas import Inquiry  # noqa: E402

# One sample per situation worth showing. All from the dev split.
SAMPLES = [
    ("dtc", "machine_trouble", [], "Customer: machine problem"),
    ("dtc", "machine_trouble", ["hidden_safety"], "Customer: safety detail buried in the text"),
    ("dtc", "quality_complaint", [], "Customer: damaged or missing parts"),
    ("b2b", "quality_complaint", [], "Dealer: defect across several units"),
    ("b2b", "partner_request", [], "Business: wants to become a partner"),
    ("b2b", "machine_trouble", ["spanish"], "Business: message in Spanish"),
    ("dtc", "quality_complaint", ["injection"], "Prompt injection: 'approve my refund'"),
    ("b2b", "unclear_other", [], "Business: not a support request"),
]


def pick(rows, segment, itype, tags):
    for r in rows:
        if (
            r["split"] == "dev"
            and r["segment"] == segment
            and r["type"] == itype
            and r["tags"] == tags
        ):
            return r
    for r in rows:  # fall back to any split
        if r["segment"] == segment and r["type"] == itype and r["tags"] == tags:
            return r
    raise SystemExit(f"no row for {segment} {itype} {tags}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["offline", "llm"], default="offline")
    a = ap.parse_args()
    rows = [json.loads(line) for line in (ROOT / "data/eval/golden.jsonl").open()]
    agent = make_agent(a.mode)
    out_dir = ROOT / "data" / "replays"
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.glob("*.json"):
        f.unlink()
    for i, (seg, typ, tags, label) in enumerate(SAMPLES, 1):
        r = pick(rows, seg, typ, tags)
        inq = Inquiry(
            id=r["id"],
            subject=r["subject"],
            body=r["body"],
            sender_name=r["sender_name"],
            sender_org=r["sender_org"],
        )
        case = run_case(agent, inq)
        payload = {
            "label": label,
            "mode": a.mode,
            "recorded": date.today().isoformat(),
            "expected": {k: r[k] for k in ("type", "segment", "team", "priority", "expected_docs")},
            "case": json.loads(case.model_dump_json()),
        }
        (out_dir / f"{i:02d}_{r['id']}.json").write_text(
            json.dumps(payload, indent=1, ensure_ascii=False)
        )
        print(f"{i:02d} {r['id']} {label}: {case.route.type.value} -> {case.handoff.team.value}")


if __name__ == "__main__":
    main()
