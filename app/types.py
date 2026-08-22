"""Shared TypedDicts for Privacy Gate.

These are the canonical data contracts used by detector, sanitiser,
reasoner, and audit modules. The API layer (api/contracts.py) mirrors
these as Pydantic models for request/response validation.

See docs/specs/privacy-gate.md §3 for the spec and ADR-011, ADR-012.
"""

from __future__ import annotations

from typing import TypedDict, Literal

FieldType = Literal[
    "name",
    "address",
    "ni_number",
    "account_number",
    "email",
    "phone",
    "date_of_birth",
    "signature",
    "personal_image",
]

ConsentAction = Literal["keep", "blacklabel", "encrypt"]


class Span(TypedDict):
    id: str
    type: str
    start: int
    end: int
    value: str
    kind: str
    image_id: str
    bbox: list[float] | None


class DetectionResult(TypedDict):
    text: str
    spans: list[Span]
    images: list[dict]
    documentName: str
    fallback_triggered: bool
    warning: str


class ConsentDecision(TypedDict):
    toggles: dict[str, str]
    passphrase: str | None


class AuditEntry(TypedDict):
    field_type: str
    decision: str
    approved_by: str
    details: str


class GeminiResult(TypedDict):
    inconsistency_detected: bool
    analysis: str
    draft_letter: str


class ChatResult(TypedDict):
    reply: str
    cited_fields: list[str]
    refused_field_types: list[str]