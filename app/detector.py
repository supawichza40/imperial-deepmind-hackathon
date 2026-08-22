"""Sensitive-field detection: deterministic regex plus a local model.

Regex catches the obvious, syntactic cases (NI numbers, postcodes, emails,
phone numbers, labelled account numbers) instantly. The model handles what
regex cannot: names in context, free-text disclosure. A 3-second timeout on
the model call means the product degrades to regex-only rather than hanging
a demo (ADR-006).

Model: `gemma4:31b-cloud`, called through the exact same native Ollama route
as a locally-pulled model — Ollama proxies the `-cloud` tag to a hosted
endpoint, so the code path here is unaffected. See
.claude/skills/privacy-gate/SKILL.md, "The local model", for why this is the
model name in force (not `gemma4:e2b` — that model was never actually pulled
on the build machine).

Gemma returns `{text, type}` pairs, never offsets: small models hallucinate
arithmetic on character positions (ADR-001). Python resolves offsets via
best-match `str.find()` with claimed-interval tracking so repeated or
out-of-order substrings resolve correctly (ADR-008). Overlapping spans are
then merged in two passes: same-type merge, then cross-type overlap
resolution keeping the longer span (ADR-002 / ADR-007).
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from app.types import DetectionResult, Span

_OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_URL = f"{_OLLAMA_HOST}/api/generate"
MODEL = os.environ.get("LOCAL_MODEL", "gemma4:e2b")
TIMEOUT_SECONDS = int(os.environ.get("LOCAL_TIMEOUT", "12"))
NUM_PREDICT = 200

# Spec §9.1 system prompt, verbatim except for the substitution marker.
_SYSTEM_PROMPT_TEMPLATE = """You are a sensitive-field detector. Find names, addresses, emails, phone numbers, dates of birth, and signatures in the text below. Return ONLY a JSON array. No explanation, no markdown.

Format:
[{"text": "exact matched substring", "type": "name|address|email|phone|date_of_birth|signature"}]

Text:
<DOCUMENT TEXT HERE>"""

# The 9 canonical field types (ADR-011). Anything Gemma returns outside this
# set (e.g. "date", "occupation") is silently dropped.
_CANONICAL_TYPES = frozenset(
    {
        "name",
        "address",
        "ni_number",
        "account_number",
        "email",
        "phone",
        "date_of_birth",
        "signature",
        "personal_image",
    }
)

# --- Regex patterns -------------------------------------------------------

_NI_RE = re.compile(r"\b[A-Za-z]{2}\d{6}[A-Za-z]\b")
_POSTCODE_RE = re.compile(r"\b[A-Za-z]{1,2}\d[A-Za-z\d]?\s*\d[A-Za-z]{2}\b")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE_RE = re.compile(r"\b(?:\+44[\s\-]*|0)7\d{3}[\s\-]?\d{6}\b")
# Context-aware: only digits after an "Account"/"Account number" label (D-11).
# Excludes bare amounts/dates like "Amount: 12345678".
_ACCOUNT_RE = re.compile(r"(?i)\baccount(?:\s+number)?\s*[:#-]?\s*(\d{3,})\b")
_NAME_LABEL_RE = re.compile(
    r"(?im)^\s*(?:employee|patient|account\s+holder|name|applicant|candidate|full\s+name)\s*:\s*(.+?)\s*$"
)
_SKIP_HEADINGS = frozenset(
    {
        "payslip",
        "invoice",
        "statement",
        "bank statement",
        "clinic letter",
        "education",
        "experience",
        "professional experience",
        "professional",
        "skills",
        "projects",
        "summary",
        "objective",
        "contact",
        "profile",
        "references",
        "employment",
        "qualifications",
        "awards",
        "interests",
        "languages",
        "certifications",
        "work history",
        "personal details",
        "curriculum vitae",
        "resume",
        "cv",
        "confidential",
    }
)


def _looks_like_person_name(value: str) -> bool:
    value = value.strip()
    if not value or len(value) > 48:
        return False
    if any(ch.isdigit() for ch in value):
        return False
    if "@" in value or "http" in value.lower():
        return False
    heading = value.lower().rstrip(":.")
    if heading in _SKIP_HEADINGS:
        return False
    words = re.findall(r"[A-Za-z][A-Za-z'.\-]*", value)
    if not (1 <= len(words) <= 4):
        return False
    leftover = re.sub(r"[A-Za-z'.\-]+", "", value)
    leftover = leftover.replace(" ", "").replace(".", "")
    if leftover:
        return False
    if value.isupper():
        return True
    return all(w[0].isupper() for w in words)


def _name_span(text: str, start: int, end: int) -> dict[str, Any]:
    return {"type": "name", "start": start, "end": end, "value": text[start:end]}


def _detect_names(text: str) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    seen: set[str] = set()
    for m in _NAME_LABEL_RE.finditer(text):
        value = m.group(1).strip()
        if not _looks_like_person_name(value):
            continue
        start, end = m.start(1), m.start(1) + len(value)
        spans.append(_name_span(text, start, end))
        seen.add(value.lower())
    for line in text.splitlines()[:12]:
        raw = line.strip()
        if not raw or raw.lower() in seen:
            continue
        heading = raw.lower().rstrip(":")
        if heading in _SKIP_HEADINGS or ":" in raw:
            continue
        if not _looks_like_person_name(raw):
            continue
        idx = text.find(raw)
        if idx == -1:
            continue
        spans.append(_name_span(text, idx, idx + len(raw)))
        break
    return spans


def _detect_regex(text: str) -> list[dict[str, Any]]:
    """Deterministic fallback. Returns plain span dicts (type/start/end/value)."""
    spans: list[dict[str, Any]] = []

    for m in _NI_RE.finditer(text):
        spans.append({"type": "ni_number", "start": m.start(), "end": m.end(), "value": m.group(0)})

    for m in _POSTCODE_RE.finditer(text):
        spans.append({"type": "address", "start": m.start(), "end": m.end(), "value": m.group(0)})

    for m in _EMAIL_RE.finditer(text):
        spans.append({"type": "email", "start": m.start(), "end": m.end(), "value": m.group(0)})

    for m in _PHONE_RE.finditer(text):
        spans.append({"type": "phone", "start": m.start(), "end": m.end(), "value": m.group(0)})

    for m in _ACCOUNT_RE.finditer(text):
        spans.append(
            {
                "type": "account_number",
                "start": m.start(1),
                "end": m.end(1),
                "value": m.group(1),
            }
        )

    spans.extend(_detect_names(text))
    return spans


# --- Gemma (native Ollama /api/generate) ----------------------------------


def _call_ollama(prompt: str) -> str:
    """Native route, not /v1 — /v1 silently ignores think:false (see SKILL.md)."""
    payload = json.dumps(
        {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "format": "json",
            "options": {"num_predict": NUM_PREDICT},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS)
    body = resp.read()
    data = json.loads(body)
    return data.get("response", "")


def _strip_code_fences(raw: str) -> str:
    cleaned = raw.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "")
    return cleaned.strip().strip("`").strip()


def _extract_json_array(s: str) -> str | None:
    start = s.find("[")
    end = s.rfind("]")
    if start == -1 or end == -1 or end < start:
        return None
    return s[start : end + 1]


def _parse_gemma_response(raw: str) -> list[Any] | None:
    """Defensive JSON parsing (FR-11). Returns None if unparseable."""
    cleaned = _strip_code_fences(raw)
    candidate = _extract_json_array(cleaned)
    if candidate is None:
        return None

    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # Fallback: pull out individual {...} objects and parse each.
    items = []
    for obj_str in re.findall(r"\{[^{}]*\}", candidate):
        try:
            items.append(json.loads(obj_str))
        except json.JSONDecodeError:
            continue
    if items:
        return items

    return None


def _overlaps_claimed(idx: int, end: int, claimed: list[tuple[int, int]]) -> bool:
    return any(idx < c_end and end > c_start for c_start, c_end in claimed)


def _find_unclaimed(text: str, needle: str, claimed: list[tuple[int, int]]) -> tuple[int, int] | None:
    """ADR-008: first occurrence of `needle` whose interval isn't already claimed.

    Exact match first, then case-insensitive, then flexible whitespace so a
    CV name split across lines still resolves.
    """
    if not needle:
        return None
    search_from = 0
    while True:
        idx = text.find(needle, search_from)
        if idx == -1:
            break
        end = idx + len(needle)
        if not _overlaps_claimed(idx, end, claimed):
            return idx, end
        search_from = idx + 1

    lower = text.lower()
    needle_l = needle.lower()
    search_from = 0
    while True:
        idx = lower.find(needle_l, search_from)
        if idx == -1:
            break
        end = idx + len(needle)
        if not _overlaps_claimed(idx, end, claimed):
            return idx, end
        search_from = idx + 1

    parts = [re.escape(p) for p in needle.split() if p]
    if len(parts) < 2:
        return None
    pattern = re.compile(r"\s+".join(parts), re.IGNORECASE)
    for match in pattern.finditer(text):
        if not _overlaps_claimed(match.start(), match.end(), claimed):
            return match.start(), match.end()
    return None


def _resolve_gemma_spans(text: str, items: list[Any]) -> list[dict[str, Any]]:
    claimed: list[tuple[int, int]] = []
    spans: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        value = item.get("text")
        raw_type = item.get("type")
        if not isinstance(value, str) or not value:
            continue
        if raw_type not in _CANONICAL_TYPES:
            continue
        pos = _find_unclaimed(text, value, claimed)
        if pos is None:
            continue
        start, end = pos
        claimed.append((start, end))
        spans.append({"type": raw_type, "start": start, "end": end, "value": text[start:end]})
    return spans


def _detect_gemma(text: str) -> tuple[list[dict[str, Any]], bool, str]:
    """Calls the local model. Returns (spans, fallback_triggered, warning)."""
    prompt = _SYSTEM_PROMPT_TEMPLATE.replace("<DOCUMENT TEXT HERE>", text)

    try:
        raw = _call_ollama(prompt)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return [], True, "Local model unavailable, used regex-only detection."

    items = _parse_gemma_response(raw)
    if items is None:
        return [], True, "Gemma output could not be parsed, used regex-only detection."

    spans = _resolve_gemma_spans(text, items)
    return spans, False, ""


# --- Merge (ADR-002 / ADR-007) ---------------------------------------------


def _merge_spans(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Two-pass merge: same-type merge, then cross-type overlap resolution."""
    # Pass 1 — same-type merge.
    by_type: dict[str, list[dict[str, Any]]] = {}
    for s in spans:
        by_type.setdefault(s["type"], []).append(s)

    merged: list[dict[str, Any]] = []
    for group in by_type.values():
        group_sorted = sorted(group, key=lambda s: s["start"])
        current: dict[str, Any] | None = None
        for s in group_sorted:
            if current is None:
                current = dict(s)
            elif s["start"] < current["end"]:
                if s["end"] > current["end"]:
                    current["end"] = s["end"]
            else:
                merged.append(current)
                current = dict(s)
        if current is not None:
            merged.append(current)

    # Pass 2 — cross-type resolution. Sort by (start asc, end desc) so a
    # longer span at the same start is considered first.
    merged_sorted = sorted(merged, key=lambda s: (s["start"], -s["end"]))
    result: list[dict[str, Any]] = []
    for s in merged_sorted:
        if result and s["start"] < result[-1]["end"]:
            last = result[-1]
            if s["type"] == last["type"]:
                last["end"] = max(last["end"], s["end"])
                continue
            len_s = s["end"] - s["start"]
            len_last = last["end"] - last["start"]
            if len_s > len_last:
                result[-1] = s
            # else: keep `last`, drop `s`.
        else:
            result.append(s)
    return result


# --- Public API -------------------------------------------------------------


def detect(text: str) -> DetectionResult:
    """Pure function. Regex first, then Gemma. Merges results, resolves offsets."""
    regex_spans = _detect_regex(text)
    gemma_spans, fallback, warning = _detect_gemma(text)
    merged = _merge_spans(regex_spans + gemma_spans)

    spans: list[Span] = []
    counters: dict[str, int] = {}
    for s in sorted(merged, key=lambda sp: sp["start"]):
        counters[s["type"]] = counters.get(s["type"], 0) + 1
        span_id = f"{s['type']}-{counters[s['type']]}"
        spans.append(
            Span(
                id=span_id,
                type=s["type"],
                start=s["start"],
                end=s["end"],
                value=s["value"],
                kind="text",
                image_id="",
                bbox=None,
            )
        )

    return DetectionResult(
        text=text,
        spans=spans,
        images=[],
        documentName="",
        fallback_triggered=fallback,
        warning=warning,
    )
