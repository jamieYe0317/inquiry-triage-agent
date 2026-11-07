"""Join the label specs with the written inquiries, check the data, and write golden.jsonl.

Run: uv run python scripts/build_golden.py
Exits with an error if a hard check fails. Prints warnings for soft checks.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

from triage.catalog import DOC_IDS

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "data" / "eval" / "specs.jsonl"
RAW = ROOT / "data" / "eval" / "raw"
OUT = ROOT / "data" / "eval" / "golden.jsonl"

LABEL_WORDS = re.compile(
    r"machine_trouble|partner_request|quality_complaint|unclear_other|\btriage\b|\bDTC\b|\bB2B\b"
)
REAL_BRANDS = re.compile(
    r"\b(home depot|lowe'?s|tractor supply|stihl|husqvarna|honda|john deere|amazon|walmart|"
    r"briggs|kohler|generac|champion|dewalt|ryobi|craftsman|kubota|echo|toro|cub cadet|"
    r"harbor freight|menards|ace hardware|true value|ups|fedex|google|facebook)\b",
    re.IGNORECASE,
)
EMAIL = re.compile(r"[\w.+-]+@([\w-]+\.[\w.-]+)")
PHONE = re.compile(r"\(?\b\d{3}\)?[\s.-]?(\d{3})[\s.-]?\d{4}\b")


def shingles(text: str, n: int = 5) -> set[str]:
    words = re.findall(r"\w+", text.lower())
    return {" ".join(words[i : i + n]) for i in range(max(1, len(words) - n + 1))}


def main() -> int:
    specs = {s["id"]: s for s in map(json.loads, SPECS.open())}
    written: dict[str, dict] = {}
    for f in sorted(RAW.glob("batch_*.jsonl")):
        for line in f.open():
            if line.strip():
                r = json.loads(line)
                written[r["id"]] = r
    errors: list[str] = []
    warnings: list[str] = []

    missing = sorted(set(specs) - set(written))
    extra = sorted(set(written) - set(specs))
    if missing:
        errors.append(f"{len(missing)} specs have no text: {missing[:10]}")
    if extra:
        errors.append(f"{len(extra)} texts have no spec: {extra[:10]}")

    rows = []
    for sid, s in specs.items():
        w = written.get(sid)
        if not w:
            continue
        text = f"{w.get('subject') or ''}\n{w['body']}"
        if not w["body"].strip():
            errors.append(f"{sid}: empty body")
        if LABEL_WORDS.search(text):
            errors.append(f"{sid}: contains a label word")
        if m := REAL_BRANDS.search(text + " " + (w.get("sender_org") or "")):
            warnings.append(f"{sid}: possible real brand '{m.group(0)}'")
        for dom in EMAIL.findall(text):
            if not dom.lower().rstrip(".").endswith("example.com"):
                errors.append(f"{sid}: non-example email domain {dom}")
        for exch in PHONE.findall(text):
            if exch != "555":
                warnings.append(f"{sid}: phone number without 555 exchange")
        for d in s["expected_docs"]:
            if d not in DOC_IDS:
                errors.append(f"{sid}: unknown doc id {d}")
        org = w.get("sender_org")
        # A real web form has an optional company field. Half of the business senders leave it empty,
        # so the router must read the segment from the message itself.
        form_org = org if (org and int(sid.split("-")[1]) % 2 == 0) else None
        rows.append(
            {
                "id": sid,
                "split": s["split"],
                "segment": s["segment"],
                "type": s["type"],
                "scenario": s["scenario"],
                "product": s["product"],
                "safety": s["safety"],
                "expected_docs": s["expected_docs"],
                "team": s["team"],
                "cc": s["cc"],
                "priority": s["priority"],
                "tags": s["tags"],
                "subject": w.get("subject") or "",
                "body": w["body"],
                "sender_name": w.get("sender_name"),
                "sender_org": form_org,
            }
        )

    # Label fixes after a person reviews a row. Each fix needs a reason, so every change is visible.
    fixes_path = ROOT / "scripts" / "label_fixes.json"
    fixes = json.loads(fixes_path.read_text()) if fixes_path.exists() else {}
    from triage.handoff import decide
    from triage.schemas import InquiryType, Segment

    for r in rows:
        fx = fixes.get(r["id"])
        if not fx:
            continue
        if not fx.get("reason"):
            errors.append(f"{r['id']}: label fix has no reason")
        for k in ("type", "segment", "safety", "expected_docs"):
            if k in fx:
                r[k] = fx[k]
        h = decide(InquiryType(r["type"]), Segment(r["segment"]), r["safety"])
        r["team"], r["priority"], r["cc"] = h.team.value, h.priority.value, [t.value for t in h.cc]
        r["label_fix"] = fx["reason"]
    if fixes:
        print(f"applied {len(fixes)} label fixes from {fixes_path.name}")

    # near-duplicate texts (5-word shingles, Jaccard)
    sh = {r["id"]: shingles(r["body"]) for r in rows}
    dups = []
    for a, b in combinations(sh, 2):
        inter = len(sh[a] & sh[b])
        if inter and inter / len(sh[a] | sh[b]) > 0.5:
            dups.append((a, b))
    if dups:
        warnings.append(f"{len(dups)} near-duplicate pairs: {dups[:8]}")

    # repeated openings show template-like writing
    openings = Counter(" ".join(re.findall(r"\w+", r["body"].lower())[:3]) for r in rows)
    common = [(o, c) for o, c in openings.most_common(5) if c >= 8]
    if common:
        warnings.append(f"common 3-word openings: {common}")

    for w_ in warnings:
        print("WARN ", w_)
    for e in errors:
        print("ERROR", e)
    if errors:
        return 1
    rows.sort(key=lambda r: r["id"])
    with OUT.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows to {OUT}")
    print("by split/segment:", Counter((r["split"], r["segment"]) for r in rows))
    words = sorted(len(r["body"].split()) for r in rows)
    print(f"body words: min {words[0]}, median {words[len(words) // 2]}, max {words[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
