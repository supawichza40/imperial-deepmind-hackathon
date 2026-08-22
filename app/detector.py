"""Sensitive-field detection: deterministic regex plus a local model.

Regex catches labelled and syntactic fields instantly: names, addresses,
NI numbers, account numbers, emails, phones, dates of birth, signatures.
The local model only runs when that first pass is thin, so a drop stays
fast and the same document always yields the same spans.

Model: `gemma4:e2b` on this machine, overridable with LOCAL_MODEL. Do not
ship a `-cloud` tag on this path. See .claude/skills/privacy-gate/SKILL.md.
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

_NI_RE = re.compile(r"\b[A-Za-z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-Za-z]\b")
_POSTCODE_RE = re.compile(r"\b[A-Za-z]{1,2}\d[A-Za-z\d]?\s*\d[A-Za-z]{2}\b")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE_RE = re.compile(r"\b(?:\+44[\s\-]*|0)7\d{3}[\s\-]?\d{6}\b")
# Context-aware: only digits after an "Account"/"Account number" label (D-11).
# Excludes bare amounts/dates like "Amount: 12345678".
_ACCOUNT_RE = re.compile(r"(?i)\baccount(?:\s+number)?\s*[:#-]?\s*(\d{3,})\b")
_NAME_LABEL_RE = re.compile(
    r"(?im)^\s*(?:employee|patient|account\s+holder|name|applicant|candidate|full\s+name)\s*:\s*(.+?)\s*$"
)
_ADDRESS_LABEL_RE = re.compile(
    r"(?im)^\s*(?:address|home\s+address|residential\s+address|correspondence)\s*:\s*(.+?)\s*$"
)
_DOB_LABEL_RE = re.compile(
    r"(?im)^\s*(?:date\s+of\s+birth|d\.?o\.?b\.?|born)\s*:\s*(.+?)\s*$"
)
_PHONE_LABEL_RE = re.compile(
    r"(?im)^\s*(?:phone|tel|telephone|mobile|mob)\s*[:#]?\s*(.+?)\s*$"
)
_SIGNATURE_LABEL_RE = re.compile(
    r"(?im)^\s*(?:signature|signed|signatory)\s*:\s*(.+?)\s*$"
)
_SINCERELY_RE = re.compile(r"(?im)^\s*yours\s+(?:sincerely|faithfully)\s*,?\s*$")
_REGEX_ENOUGH = frozenset(
    {"email", "phone", "ni_number", "account_number", "address", "date_of_birth"}
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
_NAME_STOP = frozenset(
    {
        "ltd",
        "limited",
        "llc",
        "plc",
        "university",
        "college",
        "school",
        "consulting",
        "hospital",
        "clinic",
        "bank",
        "statement",
        "payslip",
        "invoice",
        "resume",
        "cv",
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
    if any(w.lower() in _NAME_STOP for w in words):
        return False
    leftover = re.sub(r"[A-Za-z'.\-]+", "", value)
    leftover = leftover.replace(" ", "").replace(".", "")
    if leftover:
        return False
    if value.isupper():
        return True
    return all(w[0].isupper() for w in words)


def _span(field_type: str, text: str, start: int, end: int) -> dict[str, Any]:
    return {"type": field_type, "start": start, "end": end, "value": text[start:end]}


def _add_labelled(
    text: str,
    pattern: re.Pattern[str],
    field_type: str,
    spans: list[dict[str, Any]],
    ok=None,
) -> None:
    for match in pattern.finditer(text):
        raw = match.group(1)
        value = raw.strip()
        if not value:
            continue
        if ok and not ok(value):
            continue
        lead = len(raw) - len(raw.lstrip())
        start = match.start(1) + lead
        end = start + len(value)
        spans.append(_span(field_type, text, start, end))


def _looks_like_dob(value: str) -> bool:
    if len(value) > 32 or not re.search(r"\d", value):
        return False
    if re.search(r"(?i)\b(?:pay|paid|period|statement)\b", value):
        return False
    return bool(
        re.search(
            r"(?i)\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}\b|\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b",
            value,
        )
    )


def _looks_like_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    return 10 <= len(digits) <= 13


def _looks_like_address(value: str) -> bool:
    if len(value) < 6 or len(value) > 120:
        return False
    if "@" in value:
        return False
    return bool(re.search(r"\d", value) or _POSTCODE_RE.search(value))


def _name_span(text: str, start: int, end: int) -> dict[str, Any]:
    return _span("name", text, start, end)


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


def _detect_signatures(text: str) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    _add_labelled(text, _SIGNATURE_LABEL_RE, "signature", spans, _looks_like_person_name)
    lines = text.splitlines()
    for i, line in enumerate(lines[:-1]):
        if not _SINCERELY_RE.match(line.strip()):
            continue
        nxt = lines[i + 1].strip()
        if _looks_like_person_name(nxt):
            idx = text.find(nxt)
            if idx != -1:
                spans.append(_span("signature", text, idx, idx + len(nxt)))
            break
    return spans


def _regex_is_enough(spans: list[dict[str, Any]]) -> bool:
    types = {s["type"] for s in spans}
    return "name" in types and len(types & _REGEX_ENOUGH) >= 2


def _detect_regex(text: str) -> list[dict[str, Any]]:
    """Deterministic first pass. Returns plain span dicts (type/start/end/value)."""
    spans: list[dict[str, Any]] = []

    for m in _NI_RE.finditer(text):
        spans.append(_span("ni_number", text, m.start(), m.end()))

    for m in _EMAIL_RE.finditer(text):
        spans.append(_span("email", text, m.start(), m.end()))

    for m in _PHONE_RE.finditer(text):
        spans.append(_span("phone", text, m.start(), m.end()))

    for m in _ACCOUNT_RE.finditer(text):
        spans.append(_span("account_number", text, m.start(1), m.end(1)))

    _add_labelled(text, _ADDRESS_LABEL_RE, "address", spans, _looks_like_address)
    for m in _POSTCODE_RE.finditer(text):
        spans.append(_span("address", text, m.start(), m.end()))

    _add_labelled(text, _DOB_LABEL_RE, "date_of_birth", spans, _looks_like_dob)
    _add_labelled(text, _PHONE_LABEL_RE, "phone", spans, _looks_like_phone)
    spans.extend(_detect_names(text))
    spans.extend(_detect_signatures(text))
    seen: set[tuple[str, int, int]] = set()
    unique: list[dict[str, Any]] = []
    for item in spans:
        key = (item["type"], item["start"], item["end"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


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
    snippet = text if len(text) <= 4000 else text[:4000]
    prompt = _SYSTEM_PROMPT_TEMPLATE.replace("<DOCUMENT TEXT HERE>", snippet)

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
    """Pure function. Regex first. Gemma only when labelled fields are thin."""
    regex_spans = _detect_regex(text)
    if _regex_is_enough(regex_spans):
        gemma_spans, fallback, warning = [], False, ""
    else:
        gemma_spans, fallback, warning = _detect_gemma(text)
    merged = _merge_spans(regex_spans + gemma_spans)
    for item in merged:
        item["value"] = text[item["start"] : item["end"]]

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
