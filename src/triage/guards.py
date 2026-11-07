"""Deterministic guards: clean the input, extract IDs, and block promises in drafts.

The output guard is the hard rule behind "the agent never promises a refund, a replacement,
a discount, a price, or partner terms". It runs on every draft, whatever wrote it.
"""

from __future__ import annotations

import html
import re

from .schemas import CaseDraft, ExtractedFields, GuardResult

MAX_INPUT_CHARS = 2000

_TAG = re.compile(r"<[^>]{1,200}>")
_WS = re.compile(r"[ \t]+")
_INJECTION = re.compile(
    r"ignore (all |any |your |the )?(previous |prior |above )?(instructions|rules)"
    r"|\bsystem\s*:|\byou are now\b|\bact as\b|\bdisregard (the|your|all)\b"
    r"|ignora (todas )?(las )?instrucciones",
    re.IGNORECASE,
)


def clean_input(text: str) -> tuple[str, list[str]]:
    """Strip markup, cap length, and flag text that looks like an instruction to an AI.

    The flag is for the case card only. It never changes the routing.
    """
    flags: list[str] = []
    stripped = _TAG.sub(" ", text)
    if stripped != text:
        flags.append("markup_removed")
    stripped = html.unescape(stripped)
    stripped = "\n".join(_WS.sub(" ", line).strip() for line in stripped.splitlines()).strip()
    if len(stripped) > MAX_INPUT_CHARS:
        stripped = stripped[:MAX_INPUT_CHARS]
        flags.append("truncated")
    if _INJECTION.search(stripped):
        flags.append("possible_prompt_injection")
    return stripped, flags


# ---------- identifier extraction ----------

_MODEL = re.compile(r"\bfh[\s\-_]?(210|340|520|p\s?90|g\s?7)(?![0-9])", re.IGNORECASE)
_SERIAL = re.compile(
    r"\b(FH[\-\s]?(?:210|340|520|P90|G7)[\-\s]?\d{2}[\-\s]?\d{4,6})\b"
    r"|(?:serial|s/n|sn|n[uú]mero de serie)\s*(?:number|no\.?|#)?\s*[:#]?\s*([A-Z0-9][A-Z0-9\-]{5,})",
    re.IGNORECASE,
)
_ORDER = re.compile(
    r"\b(FE[\-\s]?\d{5,7})\b"
    r"|(?:order|orden|pedido|po)\s*(?:number|no\.?|#|n[uú]mero)?\s*[:#]?\s*([A-Z]{0,3}-?\d{4,})",
    re.IGNORECASE,
)


def extract_fields(text: str) -> ExtractedFields:
    model = None
    m = _MODEL.search(text)
    if m:
        model = "FH-" + re.sub(r"\s", "", m.group(1)).upper()
    serial = None
    s = _SERIAL.search(text)
    if s:
        serial = (s.group(1) or s.group(2)).upper().replace(" ", "")
    order = None
    o = _ORDER.search(text)
    if o:
        order = (o.group(1) or o.group(2)).upper().replace(" ", "")
    return ExtractedFields(model=model, serial=serial, order_number=order)


# ---------- output guard ----------

# Phrases that commit Fernhollow to an outcome. Each one is a violation in any draft field.
PROMISE_PATTERNS: list[tuple[str, re.Pattern]] = [
    (
        "promise_refund",
        re.compile(
            r"\b(we|i)('ll| will| can| are going to)\s+(issue |process |give you |send you )?(a |your )?(full |partial )?refund",
            re.I,
        ),
    ),
    (
        "promise_replacement",
        re.compile(
            r"\b(we|i)('ll| will| can| are going to)\s+(send|ship|give|provide)( you)? (a |an )?(new|free|replacement)",
            re.I,
        ),
    ),
    (
        "promise_outcome",
        re.compile(
            r"\byou('ll| will)\s+(receive|get|be getting|be issued)\s+(a |an |your )?(full |partial )?"
            r"(refund|replacement|credit|new unit|exchange|discount)",
            re.I,
        ),
    ),
    (
        "claims_approval",
        re.compile(
            r"\b(is|are|has been|have been|was)\s+(now\s+)?(approved|authorized|accepted|granted)\b"
            r"|\bwe('ve| have)\s+(approved|authorized|accepted)\b|\bwe approve\b",
            re.I,
        ),
    ),
    ("guarantee", re.compile(r"\bguarantee[sd]?\b|\bpromise you\b", re.I)),
    (
        "price_or_discount",
        re.compile(
            r"\$\s?\d|\b\d{1,3}\s?%\s?(off|discount|margin)|\bdiscount of\b|\bfree of charge\b|\bat no (cost|charge)\b",
            re.I,
        ),
    ),
    (
        "partner_terms",
        re.compile(
            r"\b(exclusive|exclusivity)\b[^.]{0,40}\b(is yours|will be granted|we can give|you will have|you('ll| will) get)\b"
            r"|\byou('re| are) (now )?(an? )?(approved|authorized) (dealer|distributor|partner)",
            re.I,
        ),
    ),
]

# Internal next steps must not decide a remedy either; a person decides.
DECISION_PATTERNS: list[tuple[str, re.Pattern]] = [
    (
        "decides_remedy",
        re.compile(
            r"^\s*(issue|process|approve|grant|send|ship)\s+(a |the )?(full |partial )?"
            r"(refund|replacement|credit|discount|exclusive|free)",
            re.I,
        ),
    ),
]


def find_promises(text: str) -> list[str]:
    return [name for name, pat in PROMISE_PATTERNS if pat.search(text)]


def check_draft(draft: CaseDraft, retrieved_ids: list[str]) -> GuardResult:
    violations: list[str] = []
    texts = [
        draft.customer_ask,
        draft.category,
        draft.holding_reply,
        *draft.facts_given,
        *draft.facts_missing,
        *draft.next_steps,
    ]
    for t in texts:
        for v in find_promises(t):
            violations.append(f"{v}: {t[:120]}")
    for step in draft.next_steps:
        for name, pat in DECISION_PATTERNS:
            if pat.search(step):
                violations.append(f"{name}: {step[:120]}")
    unknown = [d for d in draft.cited_doc_ids if d not in retrieved_ids]
    if unknown:
        violations.append(f"cites_unretrieved_docs: {', '.join(unknown)}")
    if not draft.customer_ask.strip():
        violations.append("empty_field: customer_ask")
    if not draft.category.strip():
        violations.append("empty_field: category")
    if not draft.next_steps:
        violations.append("empty_field: next_steps")
    return GuardResult(passed=not violations, violations=violations)
