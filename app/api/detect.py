"""POST /api/detect: find personal-data spans in a block of text.

Deterministic regex covers the fields that have a fixed shape (NI number,
email, phone, account number, date of birth). The local model
(gemma4:e2b, native Ollama route) covers what regex cannot: a name or a
free-text address, both context-dependent. Model output is kept to a tiny
JSON object; character offsets are then resolved in Python by locating the
returned substring in the original text, per privacy-gate's rule to return
offsets rather than rewritten text.

If the local model is unreachable, detection falls back to regex only and
the response says so via `"model": "regex-only"` rather than silently
degrading.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.pipeline import LOCAL_MODEL, local_step  # noqa: E402
from app.export.fields import label_for  # noqa: E402

# --- deterministic regex layer ------------------------------------------

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+\.\w+|[\w.+-]+@[\w-]+\.\w+")
# Loose NI-number shape (2 letters, 6 digits, 1 letter). The strict spec
# excludes a handful of letters (D, F, I, Q, U, V...) from these positions,
# but sample/demo data isn't guaranteed to respect that, so match the shape
# rather than validating against the full official letter-exclusion table.
_NI_RE = re.compile(r"\b[A-Za-z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-Za-z]\b")
_PHONE_RE = re.compile(
    r"\b(?:\+44\s?7\d{3}|07\d{3}|0\d{2,4})[\s-]?\d{3,4}[\s-]?\d{3,4}\b"
)
_ACCOUNT_KEYWORD_RE = re.compile(
    r"(?i)\b(?:account(?:\s*number)?|sort\s*code)\b\s*[:\-]?\s*"
    r"([0-9][0-9 \-]{2,19}[0-9])"
)
_DOB_KEYWORD_RE = re.compile(
    r"(?i)\b(?:date of birth|dob|born)\b\s*[:\-]?\s*"
    r"([0-3]?\d[\/\-\s](?:[A-Za-z]{3,9}|[01]?\d)[\/\-\s]\d{2,4})"
)


def _regex_spans(text: str) -> list[dict]:
    spans = []
    for m in _EMAIL_RE.finditer(text):
        spans.append({"type": "email", "start": m.start(), "end": m.end()})
    for m in _NI_RE.finditer(text):
        spans.append({"type": "ni_number", "start": m.start(), "end": m.end()})
    for m in _PHONE_RE.finditer(text):
        spans.append({"type": "phone", "start": m.start(), "end": m.end()})
    for m in _ACCOUNT_KEYWORD_RE.finditer(text):
        spans.append({"type": "account_number", "start": m.start(1), "end": m.end(1)})
    for m in _DOB_KEYWORD_RE.finditer(text):
        spans.append({"type": "date_of_birth", "start": m.start(1), "end": m.end(1)})
    return spans


# --- local model layer: name + address (context-dependent) --------------

_MODEL_INSTRUCTION = (
    "You find personal details in a document. Read the text below and reply "
    "with ONLY a JSON object, no other words: "
    '{"name": "<the person\'s full name, or empty string>", '
    '"address": "<their postal address, or empty string>"}. '
    "Copy the name and address exactly as they appear in the text. If either "
    "is not present, use an empty string for it."
)


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


def _model_spans(text: str) -> tuple[list[dict], bool]:
    """Returns (spans, model_ok). model_ok is False if the local model
    could not be reached at all (caller falls back to regex-only)."""
    try:
        raw = local_step(text, instruction=_MODEL_INSTRUCTION)
    except RuntimeError:
        return [], False

    data = _extract_json(raw)
    spans = []
    for field_type, key in (("name", "name"), ("address", "address")):
        value = str(data.get(key) or "").strip()
        if not value:
            continue
        idx = text.find(value)
        if idx == -1:
            continue
        spans.append({"type": field_type, "start": idx, "end": idx + len(value)})
    return spans, True


# --- consequence copy ------------------------------------------------

_DEFAULT_CONSEQUENCE = {
    "name": "identifies you personally",
    "address": "places you at a specific door",
    "ni_number": "links straight to your tax record",
    "account_number": "lets someone set up a direct debit in your name",
    "email": "lets someone contact or impersonate you online",
    "phone": "lets someone contact or impersonate you by phone",
    "date_of_birth": "narrows down who you are",
    "signature": "can be copied onto other documents",
    "personal_image": "identifies you visually",
}

# When two types appear together in the same document, the combination is
# worse than either field alone, so it earns its own copy.
_COMBO_CONSEQUENCE = {
    frozenset({"name", "date_of_birth"}): "enough to pass a phone-banking identity check",
}


def _consequence_for(field_type: str, present_types: set[str]) -> str:
    for combo, text in _COMBO_CONSEQUENCE.items():
        if field_type in combo and combo <= present_types:
            return text
    return _DEFAULT_CONSEQUENCE.get(field_type, "personal information about you")


# --- merge + dedupe --------------------------------------------------

def _overlaps(a: dict, b: dict) -> bool:
    return a["start"] < b["end"] and b["start"] < a["end"]


def _dedupe(spans: list[dict]) -> list[dict]:
    """Drop a span that overlaps one already kept, longest match wins."""
    ordered = sorted(spans, key=lambda s: (s["end"] - s["start"]), reverse=True)
    kept: list[dict] = []
    for span in ordered:
        if not any(_overlaps(span, k) for k in kept):
            kept.append(span)
    return sorted(kept, key=lambda s: s["start"])


def detect(text: str) -> dict:
    """Runs regex + local-model detection over `text`.

    Returns {"spans": [...], "model": "<model id>" | "regex-only",
    "elapsed_ms": int}.
    """
    started = time.monotonic()
    spans = _regex_spans(text)
    model_spans, model_ok = _model_spans(text)
    spans.extend(model_spans)
    spans = _dedupe(spans)

    present_types = {s["type"] for s in spans}
    result_spans = []
    for span in spans:
        field_type = span["type"]
        result_spans.append({
            "type": field_type,
            "label": label_for(field_type),
            "consequence": _consequence_for(field_type, present_types),
            "start": span["start"],
            "end": span["end"],
            "value": text[span["start"]:span["end"]],
        })

    elapsed_ms = int((time.monotonic() - started) * 1000)
    return {
        "spans": result_spans,
        "model": LOCAL_MODEL if model_ok else "regex-only",
        "elapsed_ms": elapsed_ms,
    }
