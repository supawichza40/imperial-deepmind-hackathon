"""Audit builder tests (testing.md §6)."""

from app.audit import build_audit


def test_audit_one_entry_per_field_type():
    """FR-22: one audit entry per field type present in spans."""
    all_spans = {
        "payslip": [
            {"type": "name", "start": 0, "end": 5, "value": "Alice"},
            {"type": "email", "start": 10, "end": 25, "value": "alice@example.com"},
        ]
    }
    toggles = {"name": "blacklabel", "email": "keep"}
    entries = build_audit(all_spans, toggles)
    assert len(entries) == 2
    types = {e["field_type"] for e in entries}
    assert types == {"name", "email"}


def test_audit_correct_decision_per_type():
    """FR-22: 'shared' for keep, 'kept_local' for blacklabel/encrypt."""
    all_spans = {"payslip": [{"type": "name", "start": 0, "end": 5, "value": "Alice"}]}
    toggles = {"name": "blacklabel"}
    entries = build_audit(all_spans, toggles)
    name_entry = [e for e in entries if e["field_type"] == "name"][0]
    assert name_entry["decision"] == "kept_local"


def test_audit_keep_decision_is_shared():
    """A 'keep' toggle means the field is shared with the cloud step."""
    all_spans = {"payslip": [{"type": "email", "start": 0, "end": 5, "value": "a@b.com"}]}
    toggles = {"email": "keep"}
    entries = build_audit(all_spans, toggles)
    entry = [e for e in entries if e["field_type"] == "email"][0]
    assert entry["decision"] == "shared"
    assert entry["approved_by"] == "user"


def test_audit_encrypt_decision_is_kept_local():
    all_spans = {"payslip": [{"type": "ni_number", "start": 0, "end": 5, "value": "QQ"}]}
    toggles = {"ni_number": "encrypt"}
    entries = build_audit(all_spans, toggles)
    entry = [e for e in entries if e["field_type"] == "ni_number"][0]
    assert entry["decision"] == "kept_local"


def test_audit_includes_fallback_entry():
    """FR-10: fallback_triggered adds a special audit entry."""
    all_spans = {"payslip": [{"type": "name", "start": 0, "end": 5, "value": "Alice"}]}
    toggles = {"name": "keep"}
    detection_results = {
        "payslip": {"spans": [], "fallback_triggered": True, "warning": "Model unavailable"}
    }
    entries = build_audit(all_spans, toggles, detection_results)
    fallback = [e for e in entries if e["decision"] == "fallback"]
    assert len(fallback) == 1
    assert "Model unavailable" in fallback[0]["details"]
    assert fallback[0]["approved_by"] == "system"
    assert fallback[0]["field_type"] == "detector"


def test_audit_no_fallback_entry_when_healthy():
    """No fallback entry when fallback_triggered is False."""
    all_spans = {"payslip": [{"type": "name", "start": 0, "end": 5, "value": "Alice"}]}
    toggles = {"name": "keep"}
    detection_results = {"payslip": {"spans": [], "fallback_triggered": False, "warning": ""}}
    entries = build_audit(all_spans, toggles, detection_results)
    assert not any(e["decision"] == "fallback" for e in entries)


def test_audit_multi_doc_unions_field_types():
    """Multi-doc: field types are unioned across documents."""
    all_spans = {
        "payslip": [{"type": "name", "start": 0, "end": 5, "value": "Alice"}],
        "bank": [{"type": "account_number", "start": 0, "end": 8, "value": "12345678"}],
    }
    toggles = {"name": "blacklabel", "account_number": "blacklabel"}
    entries = build_audit(all_spans, toggles)
    types = {e["field_type"] for e in entries}
    assert types == {"name", "account_number"}


def test_audit_no_detection_results_no_crash():
    """build_audit works with detection_results omitted entirely."""
    all_spans = {"payslip": [{"type": "name", "start": 0, "end": 5, "value": "Alice"}]}
    toggles = {"name": "keep"}
    entries = build_audit(all_spans, toggles)
    assert len(entries) == 1
