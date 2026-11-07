"""Hand-off rules. Code, not the LLM, decides the team and the priority.

The same function labels the golden set (from the true type, segment, and safety flag)
and routes live cases (from the router's decision). So hand-off accuracy measures whether
the router got the inputs right, under one written rulebook.
"""

from __future__ import annotations

from .schemas import ExtractedFields, Handoff, InquiryType, Priority, Segment, Team

TEAM_TABLE: dict[tuple[InquiryType, Segment], Team] = {
    (InquiryType.machine_trouble, Segment.dtc): Team.service_desk,
    (InquiryType.machine_trouble, Segment.b2b): Team.service_desk,
    (InquiryType.quality_complaint, Segment.dtc): Team.customer_care,
    (InquiryType.quality_complaint, Segment.b2b): Team.quality_team,
    (InquiryType.partner_request, Segment.dtc): Team.partner_team,
    (InquiryType.partner_request, Segment.b2b): Team.partner_team,
    (InquiryType.unclear_other, Segment.dtc): Team.front_desk,
    (InquiryType.unclear_other, Segment.b2b): Team.front_desk,
}


def decide_priority(itype: InquiryType, segment: Segment, safety_issue: bool) -> Priority:
    if safety_issue:
        return Priority.urgent
    if segment == Segment.b2b and itype in (
        InquiryType.machine_trouble,
        InquiryType.quality_complaint,
    ):
        return Priority.high
    if itype == InquiryType.unclear_other:
        return Priority.low
    return Priority.normal


def decide(
    itype: InquiryType,
    segment: Segment,
    safety_issue: bool,
    fields: ExtractedFields | None = None,
) -> Handoff:
    team = TEAM_TABLE[(itype, segment)]
    cc: list[Team] = []
    if safety_issue and team != Team.quality_team:
        cc.append(Team.quality_team)
    steps: list[str] = []
    if safety_issue:
        steps.append("Tell the sender to stop using the machine (safety escalation rule).")
    if fields is not None and itype in (InquiryType.machine_trouble, InquiryType.quality_complaint):
        if not fields.model:
            steps.append("Ask the sender for the model number.")
        if not fields.serial:
            steps.append("Ask the sender for the serial number.")
    return Handoff(
        team=team,
        cc=cc,
        priority=decide_priority(itype, segment, safety_issue),
        added_steps=steps,
    )
