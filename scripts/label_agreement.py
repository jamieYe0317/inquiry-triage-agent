"""Compare the golden labels with an independent blind label of a random sample.

Run: uv run python scripts/label_agreement.py   (writes data/eval/label_agreement.md)
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
gold = {r["id"]: r for r in map(json.loads, (ROOT / "data/eval/golden.jsonl").open())}
blind = [json.loads(line) for line in (ROOT / "data/eval/raw/blind_labels.jsonl").open()]

lines = [
    "# Label agreement: golden labels versus a blind second annotator",
    "",
    f"A second Claude agent labeled {len(blind)} random rows from `LABELING.md` alone, "
    "without the golden labels. This measures how clear the labels are. It is not a human check.",
    "",
    "| Label | Agreement |",
    "|---|---:|",
]
for k in ("type", "segment", "safety"):
    agree = sum(gold[b["id"]][k] == b[k] for b in blind)
    lines.append(f"| {k} | {agree}/{len(blind)} ({100 * agree / len(blind):.0f}%) |")
lines += ["", "## Disagreements", ""]
for b in blind:
    g = gold[b["id"]]
    diff = [
        f"{k}: golden `{g[k]}`, blind `{b[k]}`"
        for k in ("type", "segment", "safety")
        if g[k] != b[k]
    ]
    if diff:
        lines.append(
            f"- `{b['id']}` ({g['scenario']}, tags {g['tags'] or 'none'}): "
            + "; ".join(diff)
            + (f". Blind note: {b['note']}" if b.get("note") else "")
        )
(ROOT / "data/eval/label_agreement.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
