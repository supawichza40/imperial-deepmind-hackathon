"""Sanitiser tests (testing.md §4)."""

from app.sanitiser import sanitise, sanitise_multi


def test_sanitise_replaces_blacklabeled_spans():
    """FR-15: blacklabeled spans replaced with █ bars."""
    text = "Employee: A. Okafor\nPay: £2,840.00"
    spans = [
        {"type": "name", "start": 10, "end": 19, "value": "A. Okafor"},
    ]
    toggles = {"name": "blacklabel"}
    result = sanitise(text, spans, toggles)
    assert "A. Okafor" not in result
    assert "█" in result
    assert "£2,840.00" in result  # pay is untyped, stays visible


def test_sanitise_preserves_kept_spans():
    """FR-15: kept spans are left intact."""
    text = "Employee: A. Okafor\nPay: £2,840.00"
    spans = [
        {"type": "name", "start": 10, "end": 19, "value": "A. Okafor"},
    ]
    toggles = {"name": "keep"}
    result = sanitise(text, spans, toggles)
    assert "A. Okafor" in result


def test_sanitise_encrypt_uses_encrypted_placeholder():
    """ADR-012: encrypt action replaces with [ENCRYPTED <FIELD LABEL>]."""
    text = "NI: QQ123456C"
    spans = [{"type": "ni_number", "start": 4, "end": 13, "value": "QQ123456C"}]
    toggles = {"ni_number": "encrypt"}
    result = sanitise(text, spans, toggles)
    assert "QQ123456C" not in result
    assert "[ENCRYPTED" in result
    assert "NI NUMBER" in result


def test_sanitise_unmentioned_type_defaults_to_keep():
    """A span whose type has no toggle entry stays visible."""
    text = "Email: a@b.com"
    spans = [{"type": "email", "start": 7, "end": 14, "value": "a@b.com"}]
    result = sanitise(text, spans, toggles={})
    assert "a@b.com" in result


def test_sanitise_reverse_offset_preserves_earlier_spans():
    """ADR-002: reverse-offset replacement doesn't shift earlier offsets."""
    text = "AAAAABBBBB"
    spans = [
        {"type": "x", "start": 0, "end": 5, "value": "AAAAA"},
        {"type": "y", "start": 5, "end": 10, "value": "BBBBB"},
    ]
    toggles = {"x": "blacklabel", "y": "blacklabel"}
    result = sanitise(text, spans, toggles)
    assert "█" in result
    assert "AAAAA" not in result
    assert "BBBBB" not in result


def test_sanitise_all_keep_returns_original():
    """Nothing blacklabeled → text unchanged."""
    text = "Hello World"
    spans = [{"type": "name", "start": 0, "end": 5, "value": "Hello"}]
    toggles = {"name": "keep"}
    result = sanitise(text, spans, toggles)
    assert result == "Hello World"


def test_sanitise_multi_document_concatenates():
    """FR-3 + spec §3.5: multi-doc sanitise concatenates with delimiter."""
    documents = {"payslip": "Pay: £100", "bank": "Deposit: £100"}
    all_spans = {"payslip": [], "bank": []}
    toggles = {}
    result = sanitise_multi(documents, all_spans, toggles)
    assert "--- DOCUMENT: PAYSLIP ---" in result
    assert "--- DOCUMENT: BANK ---" in result
    assert "£100" in result


def test_sanitise_multi_document_redacts_per_doc():
    """Multi-doc: each doc's spans are applied independently."""
    documents = {"payslip": "Name: Alice", "bank": "Name: Bob"}
    all_spans = {
        "payslip": [{"type": "name", "start": 6, "end": 11, "value": "Alice"}],
        "bank": [{"type": "name", "start": 6, "end": 9, "value": "Bob"}],
    }
    toggles = {"name": "blacklabel"}
    result = sanitise_multi(documents, all_spans, toggles)
    assert "Alice" not in result
    assert "Bob" not in result
    assert "█" in result


def test_sanitise_handles_unsorted_spans():
    """Sanitiser must sort spans by start descending internally — input order doesn't matter."""
    text = "AAAAABBBBBCCCCC"
    spans = [
        {"type": "c", "start": 10, "end": 15, "value": "CCCCC"},
        {"type": "a", "start": 0, "end": 5, "value": "AAAAA"},
        {"type": "b", "start": 5, "end": 10, "value": "BBBBB"},
    ]
    toggles = {"a": "blacklabel", "b": "blacklabel", "c": "blacklabel"}
    result = sanitise(text, spans, toggles)
    assert "AAAAA" not in result
    assert "BBBBB" not in result
    assert "CCCCC" not in result
    assert "█" in result


def test_sanitise_black_bar_capped_at_48_chars():
    """Blacklabel bar length is capped so very long spans don't blow up the display."""
    text = "X" * 200
    spans = [{"type": "address", "start": 0, "end": 200, "value": "X" * 200}]
    toggles = {"address": "blacklabel"}
    result = sanitise(text, spans, toggles)
    assert result.count("█") <= 48
