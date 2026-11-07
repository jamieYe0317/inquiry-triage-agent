"""Retrieval policy: which document sources each inquiry type may search. Code owns this."""

from __future__ import annotations

from .schemas import InquiryType

ALLOWED_SOURCES: dict[InquiryType, tuple[str, ...]] = {
    InquiryType.machine_trouble: ("manual", "troubleshooting", "warranty"),
    InquiryType.quality_complaint: ("quality", "warranty"),
    InquiryType.partner_request: ("partner",),
    InquiryType.unclear_other: ("general",),
}

# Below this router confidence, the case goes to the Front desk as unclear, with no lookup.
LOW_CONFIDENCE = 0.4
