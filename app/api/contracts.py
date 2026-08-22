"""Pydantic request/response models for the Privacy Gate API.

Mirrors the TypedDicts in `app/types.py` (ADR-011/ADR-012 shapes) but as
Pydantic BaseModel classes for FastAPI request validation and
auto-generated OpenAPI docs. Core modules (sanitiser, audit, detector,
reasoner) still speak TypedDicts / plain dicts -- the API layer converts
at the boundary. See docs/specs/api.md §6.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DocumentInput(BaseModel):
    id: str
    text: str


class DocumentSummary(BaseModel):
    id: str
    name: str
    text: str


class DocumentsResponse(BaseModel):
    documents: list[DocumentSummary]


class SpanModel(BaseModel):
    id: str = ""
    type: str
    start: int
    end: int
    value: str = ""
    kind: str = "text"
    image_id: str = ""
    bbox: list[float] | None = None


class ImageModel(BaseModel):
    id: str
    alt: str = ""
    data_url: str = ""


class DetectionResultModel(BaseModel):
    text: str = ""
    spans: list[SpanModel] = Field(default_factory=list)
    images: list[ImageModel] = Field(default_factory=list)
    documentName: str = ""
    fallback_triggered: bool = False
    warning: str = ""


class DetectRequest(BaseModel):
    documents: list[DocumentInput] = Field(default_factory=list)


class DetectResponse(BaseModel):
    results: dict[str, DetectionResultModel]


class ConsentRequest(BaseModel):
    toggles: dict[str, str]  # {type: "keep"|"blacklabel"|"encrypt"}
    passphrase: str | None = None


class SanitiseRequest(BaseModel):
    documents: list[DocumentInput] = Field(default_factory=list)
    spans: dict[str, list[SpanModel]] = Field(default_factory=dict)
    toggles: dict[str, str] | None = None
    passphrase: str | None = None


class SanitiseResponse(BaseModel):
    sanitised_payload: str


class ReasonRequest(BaseModel):
    sanitised_payload: str = ""


class GeminiResultModel(BaseModel):
    inconsistency_detected: bool
    analysis: str
    draft_letter: str


class AuditRequest(BaseModel):
    spans: dict[str, list[SpanModel]] = Field(default_factory=dict)
    toggles: dict[str, str] = Field(default_factory=dict)
    detection_results: dict[str, DetectionResultModel] = Field(default_factory=dict)


class AuditEntryModel(BaseModel):
    field_type: str
    decision: str
    approved_by: str
    details: str


class AuditResponse(BaseModel):
    audit_log: list[AuditEntryModel]


class ErrorResponse(BaseModel):
    error: str
    detail: Any = None
