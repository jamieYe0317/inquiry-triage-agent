"""Typed data that moves through the graph."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class InquiryType(str, Enum):
    machine_trouble = "machine_trouble"
    partner_request = "partner_request"
    quality_complaint = "quality_complaint"
    unclear_other = "unclear_other"


class Segment(str, Enum):
    dtc = "dtc"
    b2b = "b2b"


class Team(str, Enum):
    service_desk = "Service desk"
    customer_care = "Customer care"
    quality_team = "Quality team"
    partner_team = "Partner team"
    front_desk = "Front desk"


class Priority(str, Enum):
    urgent = "urgent"
    high = "high"
    normal = "normal"
    low = "low"


class Inquiry(BaseModel):
    id: str = "live"
    subject: str = ""
    body: str
    sender_name: str | None = None
    sender_org: str | None = None

    def as_text(self) -> str:
        parts = []
        if self.subject:
            parts.append(f"Subject: {self.subject}")
        if self.sender_org:
            parts.append(f"Organization: {self.sender_org}")
        parts.append(self.body)
        return "\n".join(parts)


class RouterDecision(BaseModel):
    """What the router (LLM or keyword baseline) returns. Strict schema for structured output."""

    model_config = ConfigDict(extra="forbid")

    type: InquiryType
    segment: Segment
    safety_issue: bool = Field(description="True only when the text reports a risk to people.")
    confidence: float = Field(description="0 to 1. How sure the router is about the type.")
    also_mentions: list[InquiryType] = Field(
        description="Other types also present in a mixed message."
    )
    retrieve: bool
    search_query: str = Field(description="Short English search query, or empty if no retrieval.")
    reason: str = Field(description="One sentence on why this type was chosen.")


class ExtractedFields(BaseModel):
    """Identifiers that code extracts with regular expressions."""

    model: str | None = None
    serial: str | None = None
    order_number: str | None = None


class RetrievedChunk(BaseModel):
    doc_id: str
    title: str
    source_type: str
    heading: str
    text: str
    score: float


class CaseDraft(BaseModel):
    """What the drafter returns. Internal case summary for a person, not a customer reply."""

    model_config = ConfigDict(extra="forbid")

    customer_ask: str
    facts_given: list[str]
    facts_missing: list[str]
    category: str
    cited_doc_ids: list[str]
    next_steps: list[str]
    holding_reply: str = Field(
        description="Short acknowledgement a person may edit and send. No promises of any outcome."
    )


class GuardResult(BaseModel):
    passed: bool
    violations: list[str] = Field(default_factory=list)


class Handoff(BaseModel):
    team: Team
    cc: list[Team] = Field(default_factory=list)
    priority: Priority
    added_steps: list[str] = Field(default_factory=list)


class Case(BaseModel):
    inquiry: Inquiry
    input_flags: list[str] = Field(default_factory=list)
    route: RouterDecision
    fields: ExtractedFields
    retrieval_skipped_reason: str | None = None
    retrieved: list[RetrievedChunk] = Field(default_factory=list)
    draft: CaseDraft | None = None
    draft_guard: GuardResult | None = None
    draft_removed: bool = False
    handoff: Handoff
    usage: dict = Field(default_factory=dict)
    timings_ms: dict = Field(default_factory=dict)
