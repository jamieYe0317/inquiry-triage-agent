"""BM25 keyword search over the invented company documents in data/docs/.

Each "## " section is one chunk. The search returns the best chunk of each of the top-k
documents, filtered to the sources that the retrieval policy allows.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from rank_bm25 import BM25Okapi

from .schemas import RetrievedChunk

DOCS_DIR = Path(__file__).resolve().parents[2] / "data" / "docs"

_STOP = set(
    "a an and are as at be but by for from has have i if in into is it its me my of on or our so "
    "that the their them then there these they this to was we were what when which will with you "
    "your can do does did not no just also been get got any all some more very how why".split()
)
_MODEL_NORM = re.compile(r"\bfh[\s\-_]?(210|340|520|p\s?90|g\s?7)(?![0-9])", re.IGNORECASE)
_WORD = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    text = _MODEL_NORM.sub(lambda m: " fh" + re.sub(r"\s", "", m.group(1)).lower() + " ", text)
    tokens = []
    for w in _WORD.findall(text.lower()):
        if w in _STOP or len(w) < 2:
            continue
        for suf in ("ing", "ed", "es", "s"):
            if len(w) > 5 and w.endswith(suf):
                w = w[: -len(suf)]
                break
        tokens.append(w)
    return tokens


@dataclass
class Doc:
    id: str
    title: str
    source_type: str
    products: list[str]
    sections: list[tuple[str, str]]  # (heading, text)


def parse_doc(path: Path) -> Doc:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    if not m:
        raise ValueError(f"{path.name}: missing front matter")
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    products = [p.strip() for p in meta.get("products", "[]").strip("[]").split(",") if p.strip()]
    body = m.group(2)
    sections: list[tuple[str, str]] = []
    for part in re.split(r"^## ", body, flags=re.MULTILINE)[1:]:
        heading, _, text = part.partition("\n")
        sections.append((heading.strip(), text.strip()))
    if not sections:
        sections = [("", body.strip())]
    return Doc(meta["id"], meta["title"], meta["source_type"], products, sections)


class Retriever:
    def __init__(self, docs_dir: Path = DOCS_DIR):
        self.docs = {d.id: d for d in (parse_doc(p) for p in sorted(docs_dir.glob("*.md")))}
        self.chunks: list[tuple[Doc, str, str]] = []
        for doc in self.docs.values():
            for heading, text in doc.sections:
                self.chunks.append((doc, heading, text))
        corpus = [tokenize(f"{d.title} {h} {t}") for d, h, t in self.chunks]
        self.bm25 = BM25Okapi(corpus)

    def search(
        self,
        query: str,
        allowed_sources: tuple[str, ...],
        model: str | None = None,
        k: int = 3,
    ) -> list[RetrievedChunk]:
        if not allowed_sources:
            return []
        q = tokenize(query + (f" {model}" if model else ""))
        if not q:
            return []
        scores = self.bm25.get_scores(q)
        best: dict[str, tuple[float, int]] = {}
        for i, (doc, _, _) in enumerate(self.chunks):
            if doc.source_type not in allowed_sources:
                continue
            s = float(scores[i])
            # A product-specific doc about a different product is a weak match.
            if model and doc.products and model not in doc.products:
                s *= 0.3
            if s > best.get(doc.id, (-1.0, -1))[0]:
                best[doc.id] = (s, i)
        ranked = sorted(best.items(), key=lambda kv: kv[1][0], reverse=True)[:k]
        out = []
        for doc_id, (score, i) in ranked:
            if score <= 0:
                continue
            doc, heading, text = self.chunks[i]
            out.append(
                RetrievedChunk(
                    doc_id=doc_id,
                    title=doc.title,
                    source_type=doc.source_type,
                    heading=heading,
                    text=text,
                    score=round(score, 3),
                )
            )
        return out


@lru_cache(maxsize=1)
def default_retriever() -> Retriever:
    return Retriever()
