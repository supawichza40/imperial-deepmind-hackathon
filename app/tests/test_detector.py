"""Detector tests — docs/specs/testing.md §3.

Regex detection, Gemma detection (mocked Ollama), merge algorithm, offsets.
Never make live Ollama calls in these tests (see SKILL.md — the model may
still be provisioning cloud-side; mocked urlopen is the spec'd pattern).
"""

import json
from unittest.mock import patch, MagicMock

from app.detector import _detect_regex, _detect_gemma, _merge_spans, detect


# --- 3.1 Regex detection -----------------------------------------------


def test_regex_finds_ni_number(payslip_text):
    """FR-5: regex detects NI numbers."""
    spans = _detect_regex(payslip_text)
    ni_spans = [s for s in spans if s["type"] == "ni_number"]
    assert len(ni_spans) == 1
    assert ni_spans[0]["value"] == "QQ123456C"


def test_regex_finds_postcode_and_maps_to_address(payslip_text):
    """FR-5 + type mapping: postcode regex → type='address'."""
    spans = _detect_regex(payslip_text)
    address_spans = [s for s in spans if s["type"] == "address"]
    assert any("SW7" in s["value"] for s in address_spans)


def test_regex_finds_account_number_with_context(payslip_text):
    """D-11: account_number regex only matches after 'Account' label."""
    spans = _detect_regex(payslip_text)
    acct_spans = [s for s in spans if s["type"] == "account_number"]
    assert len(acct_spans) == 1
    assert acct_spans[0]["value"] == "4417"


def test_regex_does_not_false_positive_on_amounts():
    """D-11: numbers not preceded by 'Account' are not matched."""
    text = "Amount: 12345678\nDate: 20260725"
    spans = _detect_regex(text)
    acct_spans = [s for s in spans if s["type"] == "account_number"]
    assert len(acct_spans) == 0


def test_regex_finds_email():
    """FR-5: regex detects emails as their own type 'email'."""
    text = "Contact: john.doe@example.co.uk"
    spans = _detect_regex(text)
    assert any(s["type"] == "email" and "john.doe" in s["value"] for s in spans)


def test_regex_finds_phone():
    """FR-5: regex detects UK phone numbers as 'phone' type."""
    text = "Phone: 07700 900123"
    spans = _detect_regex(text)
    assert any(s["type"] == "phone" for s in spans)


def test_regex_finds_labelled_employee_name(payslip_text):
    spans = _detect_regex(payslip_text)
    names = [s for s in spans if s["type"] == "name"]
    okafor = next(s for s in names if s["value"] == "A. Okafor")
    assert payslip_text[okafor["start"]:okafor["end"]] == "A. Okafor"


def test_regex_finds_all_caps_cv_header_name():
    text = "REECE\nEDUCATION\nJain University\nPhone: 07700 900123\n"
    spans = _detect_regex(text)
    names = [s for s in spans if s["type"] == "name"]
    assert any(s["value"] == "REECE" for s in names)
    phones = [s for s in spans if s["type"] == "phone"]
    assert len(phones) == 1


def test_regex_skips_document_title_as_name():
    text = "PAYSLIP: July 2026\nNet Pay: 100\n"
    spans = _detect_regex(text)
    assert [s for s in spans if s["type"] == "name"] == []


def test_regex_spans_have_valid_offsets():
    """FR-7: span start/end map to correct text slice."""
    text = "NI: QQ123456C done"
    spans = _detect_regex(text)
    ni = [s for s in spans if s["type"] == "ni_number"][0]
    assert text[ni["start"]:ni["end"]] == "QQ123456C"


# --- 3.2 Gemma detection -------------------------------------------------


def test_gemma_returns_spans_on_success(payslip_text, mock_ollama_success):
    """FR-6: Gemma returns {text, type} pairs, Python resolves offsets."""
    spans, fallback, warning = _detect_gemma(payslip_text)
    assert fallback is False
    assert len(spans) == 2
    assert any(s["type"] == "name" and s["value"] == "A. Okafor" for s in spans)
    assert any(s["type"] == "address" for s in spans)


def test_gemma_offsets_match_text(payslip_text, mock_ollama_success):
    """ADR-001: offsets resolved via str.find match the text."""
    spans, _, _ = _detect_gemma(payslip_text)
    for span in spans:
        assert payslip_text[span["start"]:span["end"]] == span["value"]


def test_gemma_timeout_triggers_fallback(payslip_text, mock_ollama_timeout):
    """FR-10 + NFR-5: Ollama timeout → fallback=True, regex-only."""
    spans, fallback, warning = _detect_gemma(payslip_text)
    assert fallback is True
    assert "regex-only" in warning.lower() or "unavailable" in warning.lower()
    assert spans == []


def test_gemma_drops_unmapped_date_type(payslip_text, mock_ollama_success):
    """Type mapping: Gemma 'date' type that is not date_of_birth is dropped."""
    mock_response = {
        "response": '[{"text": "July 2026", "type": "date"}, {"text": "A. Okafor", "type": "name"}]'
    }
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        spans, _, _ = _detect_gemma(payslip_text)
    assert all(s["type"] != "date" for s in spans)
    assert any(s["type"] == "name" for s in spans)


def test_gemma_case_insensitive_offset():
    text = "Candidate REECE on the first line."
    mock_response = {"response": '[{"text": "Reece", "type": "name"}]'}
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        spans, fallback, _ = _detect_gemma(text)
    assert fallback is False
    assert spans[0]["value"] == "REECE"
    assert text[spans[0]["start"]:spans[0]["end"]] == "REECE"


def test_gemma_strips_json_code_fences(payslip_text):
    """FR-11: markdown ```json wrappers are stripped before parsing."""
    mock_response = {
        "response": '```json\n[{"text": "A. Okafor", "type": "name"}]\n```'
    }
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        spans, fallback, _ = _detect_gemma(payslip_text)
    assert len(spans) == 1
    assert spans[0]["value"] == "A. Okafor"


def test_gemma_malformed_json_falls_back(payslip_text):
    """FR-11: completely unparseable output → fallback."""
    mock_response = {"response": "I cannot help with that."}
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        spans, fallback, warning = _detect_gemma(payslip_text)
    assert fallback is True
    assert spans == []


def test_gemma_best_match_resolves_repeated_substrings():
    """ADR-008: repeated substrings resolved via claimed-interval tracking."""
    text = "Pelham St\nPelham Consulting\nPelham Rent"
    mock_response = {
        "response": '[{"text": "Pelham", "type": "name"}, {"text": "Pelham", "type": "name"}, {"text": "Pelham", "type": "name"}]'
    }
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        spans, _, _ = _detect_gemma(text)
    assert len(spans) == 3
    offsets = [s["start"] for s in spans]
    assert len(set(offsets)) == 3  # all at different positions


def test_gemma_empty_array_is_not_fallback():
    """Gemma returning [] (no sensitive fields) is valid, not a fallback."""
    mock_response = {"response": "[]"}
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        spans, fallback, warning = _detect_gemma("nothing sensitive here")
    assert fallback is False
    assert spans == []


def test_gemma_unknown_type_dropped():
    """Type mapping: unknown Gemma types not in the 9 canonical types are silently dropped."""
    mock_response = {
        "response": '[{"text": "something", "type": "occupation"}, {"text": "A. Okafor", "type": "name"}]'
    }
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        spans, _, _ = _detect_gemma("occupation: something, name: A. Okafor")
    assert all(s["type"] != "occupation" for s in spans)
    assert any(s["type"] == "name" for s in spans)


# --- 3.3 Merge algorithm --------------------------------------------------


def test_merge_same_type_overlapping():
    """ADR-007 pass 1: overlapping same-type spans merge."""
    spans = [
        {"type": "address", "start": 0, "end": 10, "value": "14 Pelham"},
        {"type": "address", "start": 8, "end": 20, "value": "St, London"},
    ]
    merged = _merge_spans(spans)
    assert len(merged) == 1
    assert merged[0]["start"] == 0
    assert merged[0]["end"] == 20


def test_merge_different_type_keeps_longer():
    """ADR-007 pass 2: overlapping different-type spans → keep longer."""
    spans = [
        {"type": "address", "start": 0, "end": 14, "value": "14 Pelham St,"},
        {"type": "name", "start": 8, "end": 20, "value": "St, London SW"},
    ]
    merged = _merge_spans(spans)
    assert len(merged) == 1
    # address len=14, name len=12 → address wins
    assert merged[0]["type"] == "address"


def test_merge_non_overlapping_kept_separate():
    """Non-overlapping spans are not merged."""
    spans = [
        {"type": "name", "start": 0, "end": 10, "value": "A. Okafor"},
        {"type": "email", "start": 50, "end": 70, "value": "a.okafor@example.com"},
    ]
    merged = _merge_spans(spans)
    assert len(merged) == 2


def test_merge_transitive_chain():
    """ADR-007: three chained overlaps (A→B→C) all merge correctly."""
    spans = [
        {"type": "address", "start": 0, "end": 10, "value": "aaaaaaaaaa"},
        {"type": "address", "start": 5, "end": 15, "value": "bbbbbbbbbb"},
        {"type": "address", "start": 12, "end": 20, "value": "cccccccc"},
    ]
    merged = _merge_spans(spans)
    assert len(merged) == 1
    assert merged[0]["start"] == 0
    assert merged[0]["end"] == 20


def test_merge_tie_breaker_same_start():
    """Spec §3.6 rule 4: same start, larger end wins."""
    spans = [
        {"type": "name", "start": 0, "end": 10, "value": "aaaaaaaaaa"},
        {"type": "address", "start": 0, "end": 15, "value": "aaaaaaaaaaaaaaa"},
    ]
    merged = _merge_spans(spans)
    assert len(merged) == 1
    assert merged[0]["end"] == 15  # larger end wins


def test_detect_returns_detection_result(payslip_text, mock_ollama_success):
    """FR-7: detect() returns DetectionResult with spans + fallback metadata."""
    result = detect(payslip_text)
    assert "spans" in result
    assert "fallback_triggered" in result
    assert "warning" in result
    assert isinstance(result["spans"], list)


def test_detect_falls_back_to_regex_only(payslip_text, mock_ollama_timeout):
    """FR-10: with Ollama down, detect returns regex-only spans + fallback flag."""
    result = detect(payslip_text)
    assert result["fallback_triggered"] is True
    assert len(result["spans"]) > 0  # regex still found things
    # No Gemma-only types (name, income) — only regex types
    types = {s["type"] for s in result["spans"]}
    assert "ni_number" in types  # regex finds this
