"""Public demo: sort a website inquiry for an invented equipment distributor.

Samples replay saved runs (free). "Write your own" runs the agent live, with limits.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from triage.schemas import Case, Inquiry  # noqa: E402

SESSION_LIMIT = 10
DAILY_LIMIT = int(os.environ.get("TRIAGE_DAILY_LIMIT", "100"))
REPLAYS = ROOT / "data" / "replays"
RESULTS = ROOT / "eval" / "results"

st.set_page_config(page_title="Inquiry Triage Agent", page_icon="📨", layout="wide")

# Streamlit Cloud keeps the key in its secrets page. Copy it into the environment for the SDK.
try:
    if "ANTHROPIC_API_KEY" in st.secrets and not os.environ.get("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except Exception:  # no secrets file on a local run
    pass

from triage.graph import make_agent, run_case  # noqa: E402
from triage.llm import DEFAULT_MODEL, has_api_key  # noqa: E402


@st.cache_resource
def offline_agent():
    return make_agent("offline")


@st.cache_resource
def llm_agent():
    return make_agent("llm")


@st.cache_resource
def daily_counter() -> dict:
    return {"date": date.today().isoformat(), "count": 0}


def live_runs_left() -> int:
    c = daily_counter()
    if c["date"] != date.today().isoformat():
        c["date"], c["count"] = date.today().isoformat(), 0
    return min(SESSION_LIMIT - st.session_state.get("live_runs", 0), DAILY_LIMIT - c["count"])


TEAM_ICON = {
    "Service desk": "🔧",
    "Customer care": "📦",
    "Quality team": "🧪",
    "Partner team": "🤝",
    "Front desk": "🗂️",
}
PRIORITY_ICON = {"urgent": "🔴", "high": "🟠", "normal": "🔵", "low": "⚪"}


def render_case(case: Case, mode_note: str, expected: dict | None = None) -> None:
    r, h = case.route, case.handoff
    st.caption(mode_note)
    # Plain text, not st.metric: metric values are cut off with "..." on narrow screens.
    tiles = [
        ("Type", r.type.value.replace("_", " ")),
        ("Sender", "Business (B2B)" if r.segment.value == "b2b" else "Customer (DTC)"),
        ("Team", f"{TEAM_ICON.get(h.team.value, '')} {h.team.value}"),
        ("Priority", f"{PRIORITY_ICON[h.priority.value]} {h.priority.value}"),
    ]
    for col, (label, value) in zip(st.columns(4), tiles, strict=True):
        col.caption(label)
        col.markdown(f"#### {value}")
    notes = []
    if r.safety_issue:
        notes.append("⚠️ **Safety issue.** Copied to the Quality team.")
    if h.cc:
        notes.append("Copy to: " + ", ".join(t.value for t in h.cc))
    if case.input_flags:
        notes.append("Input flags: " + ", ".join(f"`{f}`" for f in case.input_flags))
    if r.also_mentions:
        notes.append("Also mentions: " + ", ".join(t.value for t in r.also_mentions))
    notes.append(f"Router confidence {r.confidence:.2f}. {r.reason}")
    st.markdown("  \n".join(notes))
    if expected:
        ok = expected["type"] == r.type.value and expected["team"] == h.team.value
        st.markdown(
            f"{'✅' if ok else '❌'} Golden label: `{expected['type']}` → **{expected['team']}**, "
            f"`{expected['priority']}`. Expected docs: {', '.join(expected['expected_docs']) or 'none'}."
        )

    left, right = st.columns([3, 2])
    with left:
        st.subheader("Case summary for the team")
        if case.draft_removed or case.draft is None:
            st.error(
                "The draft failed the safety check and was removed. A person writes it by hand.\n\n"
                + "\n".join(
                    f"- {v}" for v in (case.draft_guard.violations if case.draft_guard else [])
                )
            )
        if case.draft:
            d = case.draft
            st.markdown(f"**Ask:** {d.customer_ask}  \n**Category:** {d.category}")
            st.markdown("**Facts given:** " + ("; ".join(d.facts_given) or "none"))
            st.markdown("**Facts missing:** " + ("; ".join(d.facts_missing) or "none"))
            st.markdown(
                "**Next steps:**\n" + "\n".join(f"1. {s}" for s in [*d.next_steps, *h.added_steps])
            )
            if not case.draft_removed:
                st.markdown("**Holding reply** (a person edits and sends it):")
                st.info(d.holding_reply)
    with right:
        st.subheader("Documents looked up")
        if case.retrieval_skipped_reason or not case.retrieved:
            st.write(case.retrieval_skipped_reason or "No document matched.")
        for c in case.retrieved:
            with st.expander(f"`{c.doc_id}` · {c.heading} (score {c.score})"):
                st.markdown(f"*{c.title}*\n\n{c.text}")
        cost = sum(u.get("cost_usd", 0) for u in case.usage.values())
        tokens = sum(
            u.get("input_tokens", 0) + u.get("output_tokens", 0) for u in case.usage.values()
        )
        total_ms = sum(case.timings_ms.values())
        st.caption(f"Time {total_ms / 1000:.1f} s · tokens {tokens} · cost ${cost:.4f}")


st.title("📨 Inquiry Triage Agent")
st.markdown(
    "An AI agent sorts website inquiries for **Fernhollow Equipment Supply**, an invented "
    "distributor of outdoor power equipment. It decides what each message is, looks up the right "
    "manual or policy, drafts a case summary, and hands the case to the right team. "
    "**A person always owns the reply.** The agent never promises a refund, a replacement, a price, "
    "or partner terms. All data here is synthetic."
)

tab_samples, tab_live, tab_how = st.tabs(
    ["Try a sample", "Write your own", "How it works and results"]
)

with tab_samples:
    files = sorted(REPLAYS.glob("*.json"))
    if not files:
        st.warning("No saved samples yet. Run `scripts/make_replays.py`.")
    else:
        payloads = [json.loads(f.read_text()) for f in files]
        choice = st.radio(
            "Pick an inquiry",
            range(len(payloads)),
            format_func=lambda i: payloads[i]["label"],
            horizontal=True,
        )
        p = payloads[choice]
        case = Case.model_validate(p["case"])
        with st.container(border=True):
            st.markdown(f"**{case.inquiry.subject or '(no subject)'}**")
            if case.inquiry.sender_org:
                st.caption(f"Company field: {case.inquiry.sender_org}")
            st.text(case.inquiry.body)
        mode = (
            f"the LLM agent ({p['case']['usage'].get('router', {}).get('model', DEFAULT_MODEL)})"
            if p["mode"] == "llm"
            else "the no-LLM baseline (keyword router + template drafter)"
        )
        render_case(
            case,
            f"Saved run of {mode}, recorded {p['recorded']}. Costs nothing to view.",
            p["expected"],
        )

with tab_live:
    live_ok = has_api_key() and live_runs_left() > 0
    if not has_api_key():
        st.info("No API key is set, so this tab runs the free no-LLM baseline.")
    elif live_runs_left() <= 0:
        st.info("The live limit is reached for now. This tab runs the free no-LLM baseline.")
    else:
        st.caption(f"Live runs left for you: {live_runs_left()}. Model: {DEFAULT_MODEL}.")
    with st.form("live"):
        subject = st.text_input("Subject", max_chars=150)
        org = st.text_input("Company (optional)", max_chars=100)
        body = st.text_area(
            "Message",
            max_chars=2000,
            height=180,
            placeholder="Example: My FH-340 chipper keeps jamming when I feed it fresh branches. What can I check?",
        )
        submitted = st.form_submit_button("Sort this inquiry")
    if submitted and body.strip():
        inq = Inquiry(subject=subject, body=body, sender_org=org or None)
        if live_ok:
            st.session_state["live_runs"] = st.session_state.get("live_runs", 0) + 1
            daily_counter()["count"] += 1
            try:
                with st.spinner("Sorting..."):
                    case = run_case(llm_agent(), inq)
                render_case(case, f"Live run of the LLM agent ({DEFAULT_MODEL}).")
            except Exception as e:  # show the baseline instead of a stack trace
                st.warning(
                    f"The LLM call failed ({type(e).__name__}). Showing the baseline instead."
                )
                render_case(run_case(offline_agent(), inq), "Live run of the no-LLM baseline.")
        else:
            render_case(run_case(offline_agent(), inq), "Live run of the no-LLM baseline.")

with tab_how:
    st.markdown(
        (ROOT / "docs" / "how-it-works.md").read_text()
        if (ROOT / "docs" / "how-it-works.md").exists()
        else ""
    )
    latest = sorted(RESULTS.glob("*.md"))
    if latest:
        pick = st.selectbox("Eval report", [p.name for p in reversed(latest)])
        st.markdown((RESULTS / pick).read_text())
