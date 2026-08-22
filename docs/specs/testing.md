# Privacy Gate — Testing Spec

**What this is:** TDD strategy and test definitions for Privacy Gate.
**Approach:** Test-driven development. Tests are written before implementation. Every module and API endpoint has tests defined here first.
**Framework:** `pytest` + `pytest-asyncio` + FastAPI `TestClient` (httpx).

---

## 1. TDD workflow

```
1. Write the test (from this spec)
2. Run it → it fails (module/endpoint doesn't exist yet)
3. Implement the module/endpoint
4. Run it → it passes
5. Refactor if needed
6. Move to the next test
```

**Rule:** no production code is written without a failing test first. The only exception is `types.py` (TypedDicts have no behaviour to test) and `fixtures.py` (data, not logic).

---

## 2. Test infrastructure

### 2.1 conftest.py — shared fixtures

```python
import json
import urllib.error
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@pytest.fixture
def payslip_text():
    from app.fixtures import PAYSLIP
    return PAYSLIP

@pytest.fixture
def bank_statement_text():
    from app.fixtures import BANK_STATEMENT
    return BANK_STATEMENT

@pytest.fixture
def api_client():
    from app.api.main import app
    return TestClient(app)

@pytest.fixture
def mock_ollama_success():
    """Mock Ollama returning valid JSON spans."""
    mock_response = {
        "response": '[{"text": "A. Okafor", "type": "name"}, {"text": "£2,840.00", "type": "income"}]'
    }
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        yield mock

@pytest.fixture
def mock_ollama_timeout():
    """Mock Ollama timing out — triggers regex-only fallback."""
    import urllib.request
    with patch("app.detector.urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        yield

@pytest.fixture
def mock_gemini_success():
    """Mock Gemini returning a valid inconsistency finding."""
    with patch("app.reasoner.get_client") as mock:
        client = MagicMock()
        resp = MagicMock()
        resp.output_text = '{"inconsistency_detected": true, "analysis": "Net pay mismatch", "draft_letter": "Dear HR..."}'
        client.interactions.create.return_value = resp
        mock.return_value = client
        yield mock

@pytest.fixture
def mock_gemini_failure():
    """Mock Gemini failing after all retries."""
    with patch("app.reasoner.get_client") as mock:
        client = MagicMock()
        client.interactions.create.side_effect = Exception("503 Service Unavailable")
        mock.return_value = client
        yield mock
```

### 2.2 Test file mapping

| Test file | Tests | Module under test |
|---|---|---|
| `test_detector.py` | Regex detection, Gemma detection, merge, fallback, JSON parsing | `detector.py` |
| `test_sanitiser.py` | Redaction, reverse-offset, multi-doc, overlap handling | `sanitiser.py` |
| `test_reasoner.py` | Gemini call, JSON parsing, fence stripping, retry, fallback | `reasoner.py` |
| `test_audit.py` | Audit entries, fallback entries, multi-doc | `audit.py` |
| `test_api.py` | All 5 API endpoints, error cases, validation | `api/main.py` |
| `test_e2e.py` | Full pipeline: detect → sanitise → reason → audit | All modules |

---

## 3. Detector tests (`test_detector.py`)

### 3.1 Regex detection

```python
def test_regex_finds_ni_number(payslip_text):
    """FR-5: regex detects NI numbers."""
    spans = _detect_regex(payslip_text)
    ni_spans = [s for s in spans if s["type"] == "ni_number"]
    assert len(ni_spans) == 1
    assert ni_spans[0]["text"] == "QQ123456C"

def test_regex_finds_postcode_and_maps_to_address(payslip_text):
    """FR-5 + type mapping: postcode regex → type='address'."""
    spans = _detect_regex(payslip_text)
    address_spans = [s for s in spans if s["type"] == "address"]
    assert any("SW7 2AZ" in s["text"] for s in address_spans)

def test_regex_finds_account_number_with_context(payslip_text):
    """D-11: account_number regex only matches after 'Account' label."""
    spans = _detect_regex(payslip_text)
    acct_spans = [s for s in spans if s["type"] == "account_number"]
    assert len(acct_spans) == 1
    assert acct_spans[0]["text"] == "12345678"

def test_regex_does_not_false_positive_on_amounts():
    """D-11: 8-digit numbers not preceded by 'Account' are not matched."""
    text = "Amount: 12345678\nDate: 20260725"
    spans = _detect_regex(text)
    acct_spans = [s for s in spans if s["type"] == "account_number"]
    assert len(acct_spans) == 0

def test_regex_finds_email():
    """FR-5: regex detects emails, mapped to 'address'."""
    text = "Contact: john.doe@example.co.uk"
    spans = _detect_regex(text)
    assert any(s["type"] == "address" and "john.doe" in s["text"] for s in spans)

def test_regex_spans_have_valid_offsets():
    """FR-7: span start/end map to correct text slice."""
    text = "NI: QQ123456C done"
    spans = _detect_regex(text)
    ni = [s for s in spans if s["type"] == "ni_number"][0]
    assert text[ni["start"]:ni["end"]] == "QQ123456C"
```

### 3.2 Gemma detection

```python
def test_gemma_returns_spans_on_success(payslip_text, mock_ollama_success):
    """FR-6: Gemma returns {text, type} pairs, Python resolves offsets."""
    spans, fallback, warning = _detect_gemma(payslip_text)
    assert fallback is False
    assert len(spans) == 2
    assert any(s["type"] == "name" and s["text"] == "A. Okafor" for s in spans)
    assert any(s["type"] == "income" and s["text"] == "£2,840.00" for s in spans)

def test_gemma_offsets_match_text(payslip_text, mock_ollama_success):
    """ADR-001: offsets resolved via str.find match the text."""
    spans, _, _ = _detect_gemma(payslip_text)
    for span in spans:
        assert payslip_text[span["start"]:span["end"]] == span["text"]

def test_gemma_timeout_triggers_fallback(payslip_text, mock_ollama_timeout):
    """FR-10 + NFR-5: Ollama timeout → fallback=True, regex-only."""
    spans, fallback, warning = _detect_gemma(payslip_text)
    assert fallback is True
    assert "regex-only" in warning.lower() or "unavailable" in warning.lower()
    assert spans == []

def test_gemma_drops_date_type(payslip_text, mock_ollama_success):
    """Type mapping: Gemma 'date' type is dropped."""
    mock_response = {
        "response": '[{"text": "July 2026", "type": "date"}, {"text": "A. Okafor", "type": "name"}]'
    }
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        spans, _, _ = _detect_gemma(payslip_text)
    assert all(s["type"] != "date" for s in spans)
    assert any(s["type"] == "name" for s in spans)

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
    assert spans[0]["text"] == "A. Okafor"

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
    """Type mapping: unknown Gemma types are silently dropped."""
    mock_response = {
        "response": '[{"text": "something", "type": "phone_number"}, {"text": "A. Okafor", "type": "name"}]'
    }
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        spans, _, _ = _detect_gemma("phone: something, name: A. Okafor")
    assert all(s["type"] != "phone_number" for s in spans)
    assert any(s["type"] == "name" for s in spans)
```

### 3.3 Merge algorithm

```python
def test_merge_same_type_overlapping():
    """ADR-007 pass 1: overlapping same-type spans merge."""
    spans = [
        {"type": "address", "start": 0, "end": 10, "text": "14 Pelham"},
        {"type": "address", "start": 8, "end": 20, "text": "St, London"},
    ]
    merged = _merge_spans(spans)
    assert len(merged) == 1
    assert merged[0]["start"] == 0
    assert merged[0]["end"] == 20

def test_merge_different_type_keeps_longer():
    """ADR-007 pass 2: overlapping different-type spans → keep longer."""
    spans = [
        {"type": "address", "start": 0, "end": 14, "text": "14 Pelham St,"},
        {"type": "name", "start": 8, "end": 20, "text": "St, London SW"},
    ]
    merged = _merge_spans(spans)
    assert len(merged) == 1
    # address len=14, name len=12 → address wins
    assert merged[0]["type"] == "address"

def test_merge_non_overlapping_kept_separate():
    """Non-overlapping spans are not merged."""
    spans = [
        {"type": "name", "start": 0, "end": 10, "text": "A. Okafor"},
        {"type": "income", "start": 50, "end": 60, "text": "£2,840.00"},
    ]
    merged = _merge_spans(spans)
    assert len(merged) == 2

def test_merge_transitive_chain():
    """ADR-007: three chained overlaps (A→B→C) all merge correctly."""
    spans = [
        {"type": "address", "start": 0, "end": 10, "text": "aaaaaaaaaa"},
        {"type": "address", "start": 5, "end": 15, "text": "bbbbbbbbbb"},
        {"type": "address", "start": 12, "end": 20, "text": "cccccccc"},
    ]
    merged = _merge_spans(spans)
    assert len(merged) == 1
    assert merged[0]["start"] == 0
    assert merged[0]["end"] == 20

def test_merge_tie_breaker_same_start():
    """Spec §3.6 rule 4: same start, larger end wins."""
    spans = [
        {"type": "name", "start": 0, "end": 10, "text": "aaaaaaaaaa"},
        {"type": "address", "start": 0, "end": 15, "text": "aaaaaaaaaaaaaaa"},
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
```

---

## 4. Sanitiser tests (`test_sanitiser.py`)

```python
def test_sanitise_replaces_blocked_spans():
    """FR-15: blocked spans replaced with [REDACTED]."""
    text = "Employee: A. Okafor\nPay: £2,840.00"
    spans = [
        {"type": "name", "start": 10, "end": 19, "text": "A. Okafor"},
        {"type": "income", "start": 25, "end": 35, "text": "£2,840.00"},
    ]
    result = sanitise(text, spans, blocked_types=["name"])
    assert "[REDACTED]" in result
    assert "A. Okafor" not in result
    assert "£2,840.00" in result  # income is shared, not blocked

def test_sanitise_preserves_shared_spans():
    """FR-15: shared spans are left intact."""
    text = "Employee: A. Okafor\nPay: £2,840.00"
    spans = [
        {"type": "name", "start": 10, "end": 19, "text": "A. Okafor"},
        {"type": "income", "start": 25, "end": 35, "text": "£2,840.00"},
    ]
    result = sanitise(text, spans, blocked_types=["name"], )
    assert "£2,840.00" in result

def test_sanitise_reverse_offset_preserves_earlier_spans():
    """ADR-002: reverse-offset replacement doesn't shift earlier offsets."""
    text = "AAAAABBBBB"
    spans = [
        {"type": "x", "start": 0, "end": 5, "text": "AAAAA"},
        {"type": "y", "start": 5, "end": 10, "text": "BBBBB"},
    ]
    result = sanitise(text, spans, blocked_types=["x", "y"])
    assert result == "[REDACTED][REDACTED]"

def test_sanitise_empty_blocked_types_returns_original():
    """Nothing blocked → text unchanged."""
    text = "Hello World"
    spans = [{"type": "name", "start": 0, "end": 5, "text": "Hello"}]
    result = sanitise(text, spans, blocked_types=[])
    assert result == "Hello World"

def test_sanitise_multi_document_concatenates():
    """FR-3 + spec §3.5: multi-doc sanitise concatenates with delimiter."""
    documents = {"payslip": "Pay: £100", "bank": "Deposit: £100"}
    all_spans = {"payslip": [], "bank": []}
    result = sanitise_multi(documents, all_spans, blocked_types=[])
    assert "--- DOCUMENT: PAYSLIP ---" in result
    assert "--- DOCUMENT: BANK ---" in result
    assert "£100" in result

def test_sanitise_multi_document_redacts_per_doc():
    """Multi-doc: each doc's spans are applied independently."""
    documents = {"payslip": "Name: Alice", "bank": "Name: Bob"}
    all_spans = {
        "payslip": [{"type": "name", "start": 6, "end": 11, "text": "Alice"}],
        "bank": [{"type": "name", "start": 6, "end": 9, "text": "Bob"}],
    }
    result = sanitise_multi(documents, all_spans, blocked_types=["name"])
    assert "Alice" not in result
    assert "Bob" not in result
    assert "[REDACTED]" in result

def test_sanitise_handles_unsorted_spans():
    """Sanitiser must sort spans by start descending internally — input order doesn't matter."""
    text = "AAAAABBBBBCCCCC"
    spans = [
        {"type": "c", "start": 10, "end": 15, "text": "CCCCC"},
        {"type": "a", "start": 0, "end": 5, "text": "AAAAA"},
        {"type": "b", "start": 5, "end": 10, "text": "BBBBB"},
    ]
    result = sanitise(text, spans, blocked_types=["a", "b", "c"])
    assert result == "[REDACTED][REDACTED][REDACTED]"
```

---

## 5. Reasoner tests (`test_reasoner.py`)

```python
def test_reason_returns_gemini_result(mock_gemini_success):
    """FR-20: reason() returns GeminiResult with analysis."""
    result = reason("sanitised text here")
    assert "inconsistency_detected" in result
    assert "analysis" in result
    assert "draft_letter" in result
    assert result["inconsistency_detected"] is True

def test_reason_strips_json_code_fences():
    """D-12: Gemini wraps JSON in ```json fences — must strip before parsing."""
    with patch("app.reasoner.get_client") as mock:
        client = MagicMock()
        resp = MagicMock()
        resp.output_text = '```json\n{"inconsistency_detected": false, "analysis": "All good", "draft_letter": ""}\n```'
        client.interactions.create.return_value = resp
        mock.return_value = client
        result = reason("sanitised text")
    assert result["inconsistency_detected"] is False
    assert result["analysis"] == "All good"

def test_reason_fallback_on_failure(mock_gemini_failure):
    """If Gemini fails after retries, reason() catches and returns fallback GeminiResult (not raise)."""
    result = reason("sanitised text")
    assert result["inconsistency_detected"] is False
    assert "failed" in result["analysis"].lower() or "error" in result["analysis"].lower()
    assert result["draft_letter"] == ""

def test_reason_never_receives_original_text():
    """FR-18: reason() only receives the sanitised payload — enforce by signature."""
    import inspect
    sig = inspect.signature(reason)
    params = list(sig.parameters)
    assert "payload" in params or "sanitised_payload" in params
    assert "text" not in params and "document" not in params  # no original-text param
```

---

## 6. Audit tests (`test_audit.py`)

```python
def test_audit_one_entry_per_field_type():
    """FR-22: one audit entry per field type present in spans."""
    all_spans = {
        "payslip": [
            {"type": "name", "start": 0, "end": 5, "text": "Alice"},
            {"type": "income", "start": 10, "end": 15, "text": "£100"},
        ]
    }
    decision = {"shared_types": ["income"], "blocked_types": ["name"]}
    entries = build_audit(all_spans, decision)
    assert len(entries) == 2
    types = {e["field_type"] for e in entries}
    assert types == {"name", "income"}

def test_audit_correct_decision_per_type():
    """FR-22: 'shared' for shared types, 'kept_local' for blocked types."""
    all_spans = {"payslip": [{"type": "name", "start": 0, "end": 5, "text": "Alice"}]}
    decision = {"shared_types": [], "blocked_types": ["name"]}
    entries = build_audit(all_spans, decision)
    name_entry = [e for e in entries if e["field_type"] == "name"][0]
    assert name_entry["decision"] == "kept_local"

def test_audit_includes_fallback_entry():
    """FR-10: fallback_triggered adds a special audit entry."""
    all_spans = {"payslip": [{"type": "name", "start": 0, "end": 5, "text": "Alice"}]}
    decision = {"shared_types": ["name"], "blocked_types": []}
    detection_results = {"payslip": {"spans": [], "fallback_triggered": True, "warning": "Model unavailable"}}
    entries = build_audit(all_spans, decision, detection_results)
    fallback = [e for e in entries if e["decision"] == "fallback"]
    assert len(fallback) == 1
    assert "Model unavailable" in fallback[0]["details"]

def test_audit_no_fallback_entry_when_healthy():
    """No fallback entry when fallback_triggered is False."""
    all_spans = {"payslip": [{"type": "name", "start": 0, "end": 5, "text": "Alice"}]}
    decision = {"shared_types": ["name"], "blocked_types": []}
    detection_results = {"payslip": {"spans": [], "fallback_triggered": False, "warning": ""}}
    entries = build_audit(all_spans, decision, detection_results)
    assert not any(e["decision"] == "fallback" for e in entries)

def test_audit_multi_doc_unions_field_types():
    """Multi-doc: field types are unioned across documents."""
    all_spans = {
        "payslip": [{"type": "name", "start": 0, "end": 5, "text": "Alice"}],
        "bank": [{"type": "account_number", "start": 0, "end": 8, "text": "12345678"}],
    }
    decision = {"shared_types": [], "blocked_types": ["name", "account_number"]}
    entries = build_audit(all_spans, decision)
    types = {e["field_type"] for e in entries}
    assert types == {"name", "account_number"}
```

---

## 7. API tests (`test_api.py`)

```python
def test_get_documents(api_client):
    """GET /api/documents returns fixture documents."""
    response = api_client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert len(data["documents"]) >= 1
    assert data["documents"][0]["id"] == "payslip"

def test_post_detect_returns_spans(api_client, payslip_text, mock_ollama_success):
    """POST /api/detect returns DetectionResult per document."""
    response = api_client.post("/api/detect", json={
        "documents": [{"id": "payslip", "text": payslip_text}]
    })
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "payslip" in data["results"]
    assert "spans" in data["results"]["payslip"]

def test_post_detect_empty_documents_returns_400(api_client):
    """POST /api/detect with empty documents array → 400."""
    response = api_client.post("/api/detect", json={"documents": []})
    assert response.status_code == 400

def test_post_sanitise_returns_redacted_text(api_client, payslip_text):
    """POST /api/sanitise returns sanitised payload with [REDACTED]."""
    response = api_client.post("/api/sanitise", json={
        "documents": [{"id": "payslip", "text": payslip_text}],
        "spans": {"payslip": [
            {"type": "name", "start": 25, "end": 34, "text": "A. Okafor"},
        ]},
        "consent": {"shared_types": [], "blocked_types": ["name"]}
    })
    assert response.status_code == 200
    assert "[REDACTED]" in response.json()["sanitised_payload"]
    assert "A. Okafor" not in response.json()["sanitised_payload"]

def test_post_reason_returns_analysis(api_client, mock_gemini_success):
    """POST /api/reason returns GeminiResult."""
    response = api_client.post("/api/reason", json={"sanitised_payload": "test payload"})
    assert response.status_code == 200
    data = response.json()
    assert "inconsistency_detected" in data
    assert "analysis" in data

def test_post_reason_empty_payload_returns_400(api_client):
    """POST /api/reason with empty payload → 400."""
    response = api_client.post("/api/reason", json={"sanitised_payload": ""})
    assert response.status_code == 400

def test_post_reason_returns_200_fallback_on_gemini_failure(api_client, mock_gemini_failure):
    """POST /api/reason returns 200 with fallback body when Gemini fails (not 502)."""
    response = api_client.post("/api/reason", json={"sanitised_payload": "test payload"})
    assert response.status_code == 200
    data = response.json()
    assert data["inconsistency_detected"] is False

def test_post_sanitise_all_blocked_returns_fully_redacted(api_client, payslip_text):
    """FR-26: if all types are blocked, sanitised payload is fully redacted but still returned."""
    response = api_client.post("/api/sanitise", json={
        "documents": [{"id": "payslip", "text": "Name: Alice\nPay: £100"}],
        "spans": {"payslip": [
            {"type": "name", "start": 6, "end": 11, "text": "Alice"},
            {"type": "income", "start": 18, "end": 23, "text": "£100"},
        ]},
        "consent": {"shared_types": [], "blocked_types": ["name", "income"]}
    })
    assert response.status_code == 200
    payload = response.json()["sanitised_payload"]
    assert "Alice" not in payload
    assert "£100" not in payload

def test_post_audit_returns_entries(api_client):
    """POST /api/audit returns audit log."""
    response = api_client.post("/api/audit", json={
        "spans": {"payslip": [{"type": "name", "start": 0, "end": 5, "text": "Alice"}]},
        "consent": {"shared_types": [], "blocked_types": ["name"]},
        "detection_results": {"payslip": {"spans": [], "fallback_triggered": False, "warning": ""}}
    })
    assert response.status_code == 200
    data = response.json()
    assert "audit_log" in data
    assert len(data["audit_log"]) >= 1

def test_get_root_serves_index_html(api_client):
    """GET / serves the PWA index.html."""
    response = api_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

def test_get_manifest_json(api_client):
    """GET /manifest.json serves PWA manifest."""
    response = api_client.get("/manifest.json")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Privacy Gate"
    assert "icons" in data
```

---

## 8. End-to-end test (`test_e2e.py`)

```python
def test_full_pipeline_detect_sanitise_reason_audit(api_client, payslip_text, bank_statement_text, mock_ollama_success, mock_gemini_success):
    """E2E: the complete flow from detection to audit log."""
    # 1. Detect
    detect_resp = api_client.post("/api/detect", json={
        "documents": [
            {"id": "payslip", "text": payslip_text},
            {"id": "bank_statement", "text": bank_statement_text},
        ]
    })
    assert detect_resp.status_code == 200
    detection_results = detect_resp.json()["results"]
    # Extract just the spans per doc (not the full DetectionResult) for the sanitise API
    spans = {doc_id: res["spans"] for doc_id, res in detection_results.items()}

    # 2. Sanitise (block identity, share income)
    consent = {"shared_types": ["income"], "blocked_types": ["name", "address", "ni_number", "account_number"]}
    sanitise_resp = api_client.post("/api/sanitise", json={
        "documents": [
            {"id": "payslip", "text": payslip_text},
            {"id": "bank_statement", "text": bank_statement_text},
        ],
        "spans": spans,
        "consent": consent,
    })
    assert sanitise_resp.status_code == 200
    payload = sanitise_resp.json()["sanitised_payload"]
    assert "[REDACTED]" in payload
    assert "£2,840.00" in payload or "£2,480.00" in payload  # income is shared

    # 3. Reason
    reason_resp = api_client.post("/api/reason", json={"sanitised_payload": payload})
    assert reason_resp.status_code == 200
    result = reason_resp.json()
    assert "analysis" in result

    # 4. Audit
    audit_resp = api_client.post("/api/audit", json={
        "spans": spans,
        "consent": consent,
        "detection_results": detect_resp.json()["results"],
    })
    assert audit_resp.status_code == 200
    audit_log = audit_resp.json()["audit_log"]
    assert len(audit_log) >= 5  # at least 5 field types

def test_full_pipeline_regex_fallback(api_client, payslip_text, mock_ollama_timeout, mock_gemini_success):
    """E2E: Ollama down → regex-only detection still works end-to-end, audit includes fallback entry."""
    # 1. Detect (regex-only fallback)
    detect_resp = api_client.post("/api/detect", json={
        "documents": [{"id": "payslip", "text": payslip_text}]
    })
    assert detect_resp.status_code == 200
    detection_results = detect_resp.json()["results"]
    assert detection_results["payslip"]["fallback_triggered"] is True
    assert len(detection_results["payslip"]["spans"]) > 0  # regex found something
    spans = {"payslip": detection_results["payslip"]["spans"]}

    # 2. Sanitise
    consent = {"shared_types": ["income"], "blocked_types": ["name", "address", "ni_number", "account_number"]}
    sanitise_resp = api_client.post("/api/sanitise", json={
        "documents": [{"id": "payslip", "text": payslip_text}],
        "spans": spans,
        "consent": consent,
    })
    assert sanitise_resp.status_code == 200

    # 3. Reason
    reason_resp = api_client.post("/api/reason", json={"sanitised_payload": sanitise_resp.json()["sanitised_payload"]})
    assert reason_resp.status_code == 200

    # 4. Audit — should include a fallback entry
    audit_resp = api_client.post("/api/audit", json={
        "spans": spans,
        "consent": consent,
        "detection_results": detection_results,
    })
    assert audit_resp.status_code == 200
    audit_log = audit_resp.json()["audit_log"]
    fallback_entries = [e for e in audit_log if e["decision"] == "fallback"]
    assert len(fallback_entries) == 1
```

---

## 9. Test execution

### 9.1 Run all tests
```bash
pytest app/tests/ -v
```

### 9.2 Run with coverage
```bash
pytest app/tests/ -v --cov=app --cov-report=term-missing
```

### 9.3 Run a single test file
```bash
pytest app/tests/test_detector.py -v
```

### 9.4 TDD cycle
```bash
# Write test → run → watch it fail
pytest app/tests/test_sanitiser.py::test_sanitise_replaces_blocked_spans -v
# Implement sanitise() → run → watch it pass
pytest app/tests/test_sanitiser.py::test_sanitise_replaces_blocked_spans -v
```

---

## 10. Test priorities for a 2-hour build

If time is short, tests are cut in this order (least to most important):

1. `test_e2e.py` — cut first (the manual demo covers this flow)
2. `test_api.py` — cut second (API is thin, core logic is in modules)
3. `test_reasoner.py` — cut third (depends on Gemini, mocked anyway)
4. `test_audit.py` — keep (simple, fast, high value)
5. `test_sanitiser.py` — keep (critical correctness, pure function)
6. `test_detector.py` — **never cut** (most complex, most likely to break)

---

## 11. Frontend testing

No automated frontend tests for the hackathon. Manual verification only:

1. Open `http://localhost:8000` → page loads, documents visible.
2. Click "Detect" → spans highlighted with colours.
3. Toggle consent checkboxes → sanitised payload updates.
4. Click "Send to Gemini" → analysis + draft letter appear.
5. Audit log displays correctly.
6. Chrome → Install → PWA installs and opens from home screen.
7. With wifi off → page still loads (service worker cache), detect still works (Ollama local), reason fails gracefully.

---

## Related

- [Architecture spec](architecture.md) — system architecture, test directory structure
- [API spec](api.md) — endpoint definitions being tested
- [Requirements spec](privacy-gate.md) — FR/NFR traceability
- [Design doc](design.md) — core module designs being tested