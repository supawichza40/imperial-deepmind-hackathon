"""Audit log builder.

Builds the human-readable trail of what stayed local and what was
shared, plus a system-authored entry whenever Gemma fell back to
regex-only detection (FR-10 / FR-22 -- this is a documented product
feature, not a bug to hide: the audit trail must show it).
"""

from __future__ import annotations

from app.types import AuditEntry, DetectionResult, Span

KEEP = "keep"


def build_audit(
    all_spans: dict[str, list[Span]],
    toggles: dict[str, str],
    detection_results: dict[str, DetectionResult] | None = None,
) -> list[AuditEntry]:
    """One entry per field type present (union across documents).

    decision is "shared" when the type's toggle is "keep" (the field
    stays visible in the payload sent to Gemini), else "kept_local"
    (blacklabel/encrypt -- redacted before it ever leaves the device).
    approved_by is "user" for these normal decisions.

    If `detection_results` is given, any document with
    fallback_triggered=True adds its own entry with
    approved_by="system" and details set to the warning text.
    """
    toggles = toggles or {}

    types_present: set[str] = set()
    for spans in all_spans.values():
        for span in spans:
            types_present.add(span["type"])

    entries: list[AuditEntry] = []
    for field_type in sorted(types_present):
        action = toggles.get(field_type, KEEP)
        decision = "shared" if action == KEEP else "kept_local"
        entries.append(
            AuditEntry(
                field_type=field_type,
                decision=decision,
                approved_by="user",
                details="",
            )
        )

    if detection_results:
        for result in detection_results.values():
            if result.get("fallback_triggered"):
                entries.append(
                    AuditEntry(
                        field_type="detector",
                        decision="fallback",
                        approved_by="system",
                        details=result.get("warning", ""),
                    )
                )

    return entries
