"""Sanitiser — reverse-offset redaction of document text.

Pure text-in / text-out step used before the sanitised payload goes to
Gemini for reasoning. This is deliberately separate from `app/export/`
(which builds the full downloadable zip, handles images and the
passphrase-locked vault). Sanitiser only ever produces a plain string.

Algorithm (design.md §3.4/§3.6, ADR-002/ADR-008 -- superseded token
mapping per ADR-012): spans whose type is toggled "blacklabel" or
"encrypt" are replaced; spans toggled "keep" (or any type with no
toggle entry) are left untouched. Replacement happens in reverse
offset order (right to left) so earlier offsets are never shifted by
an earlier replacement.
"""

from __future__ import annotations

from app.types import Span

BLACK_CHAR = "█"
_MAX_BAR = 48

KEEP = "keep"
BLACKLABEL = "blacklabel"
ENCRYPT = "encrypt"


def _black_bar(length: int) -> str:
    n = max(length, 1)
    return BLACK_CHAR * min(n, _MAX_BAR)


def _field_label(field_type: str) -> str:
    return field_type.replace("_", " ").upper()


def _replacement(action: str, field_type: str, original: str) -> str:
    if action == ENCRYPT:
        return f"[ENCRYPTED {_field_label(field_type)}]"
    if action == BLACKLABEL:
        return _black_bar(len(original))
    return original


def sanitise(text: str, spans: list[Span], toggles: dict[str, str]) -> str:
    """Replace spans whose toggle is blacklabel/encrypt, right to left.

    Spans with no toggle entry, or toggled "keep", are left visible.
    """
    toggles = toggles or {}
    to_redact = [
        s for s in spans if toggles.get(s["type"], KEEP) in (BLACKLABEL, ENCRYPT)
    ]
    # Reverse-offset order: largest start first so earlier offsets in
    # `out` stay valid as we go (ADR-002).
    ordered = sorted(to_redact, key=lambda s: (s["start"], s["end"]), reverse=True)

    out = text
    for span in ordered:
        start, end = span["start"], span["end"]
        if not (0 <= start <= end <= len(out)):
            continue
        action = toggles.get(span["type"], KEEP)
        original = span.get("value") or out[start:end]
        replacement = _replacement(action, span["type"], original)
        out = out[:start] + replacement + out[end:]
    return out


def sanitise_multi(
    documents: dict[str, str],
    all_spans: dict[str, list[Span]],
    toggles: dict[str, str],
) -> str:
    """Sanitise each document, concatenate with a per-document delimiter.

    Delimiter matches design.md §3.5 / api.md §2.3:
    "--- DOCUMENT: <ID UPPERCASE> ---".
    """
    parts = []
    for doc_id, text in documents.items():
        spans = all_spans.get(doc_id, [])
        sanitised = sanitise(text, spans, toggles)
        parts.append(f"--- DOCUMENT: {doc_id.upper()} ---\n{sanitised}")
    return "\n\n".join(parts)
