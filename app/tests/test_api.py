"""API tests (testing.md §7).

`mock_gemini_success` / `mock_gemini_failure` come from app/tests/conftest.py
(Developer C's reasoner fixtures) and work unmodified here because
app/reasoner.py already exists and `/api/reason` calls it directly.

`app.detector` may not exist yet (Developer A's file), so detector mocking
here injects a fake module into `sys.modules` rather than `unittest.mock.patch`-ing
an attribute on a module that might not be importable.
"""

from __future__ import annotations

import sys
import types

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api_client():
    from app.api.main import app

    return TestClient(app)


@pytest.fixture
def payslip_text():
    from app.fixtures import PAYSLIP

    return PAYSLIP


@pytest.fixture
def mock_detector(monkeypatch):
    """Install a fake app.detector module with a canned detect()."""

    def _install(spans=None, fallback_triggered=False, warning=""):
        spans = spans or []

        def fake_detect(text):
            return {
                "text": text,
                "spans": spans,
                "images": [],
                "documentName": "doc",
                "fallback_triggered": fallback_triggered,
                "warning": warning,
            }

        fake_module = types.ModuleType("app.detector")
        fake_module.detect = fake_detect
        monkeypatch.setitem(sys.modules, "app.detector", fake_module)
        return fake_detect

    return _install


# --- /api/documents ----------------------------------------------------


def test_get_documents(api_client):
    """GET /api/documents returns fixture documents."""
    response = api_client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert len(data["documents"]) >= 1
    assert data["documents"][0]["id"] == "payslip"
    ids = {d["id"] for d in data["documents"]}
    assert "medical_letter" in ids


# --- /api/detect ---------------------------------------------------------


def test_post_detect_returns_spans(api_client, payslip_text, mock_detector):
    """POST /api/detect returns DetectionResult per document."""
    mock_detector(spans=[{"id": "name-1", "type": "name", "start": 0, "end": 5, "value": "Alice"}])
    response = api_client.post(
        "/api/detect", json={"documents": [{"id": "payslip", "text": payslip_text}]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "payslip" in data["results"]
    assert "spans" in data["results"]["payslip"]
    assert data["results"]["payslip"]["spans"][0]["type"] == "name"


def test_post_detect_empty_documents_returns_400(api_client):
    """POST /api/detect with empty documents array → 400."""
    response = api_client.post("/api/detect", json={"documents": []})
    assert response.status_code == 400


def test_post_detect_missing_field_returns_422(api_client):
    """POST /api/detect with a document missing 'text' → 422."""
    response = api_client.post("/api/detect", json={"documents": [{"id": "payslip"}]})
    assert response.status_code == 422


def test_post_detect_survives_missing_detector(api_client, payslip_text, monkeypatch):
    """If app.detector cannot be imported, the endpoint still returns 200 (defensive import)."""
    monkeypatch.setitem(sys.modules, "app.detector", None)  # forces ImportError
    response = api_client.post(
        "/api/detect", json={"documents": [{"id": "payslip", "text": payslip_text}]}
    )
    assert response.status_code == 200
    assert response.json()["results"]["payslip"]["spans"] == []


# --- /api/sanitise ---------------------------------------------------------


def test_post_sanitise_returns_redacted_text(api_client, payslip_text):
    """POST /api/sanitise returns sanitised payload with █ bars."""
    response = api_client.post(
        "/api/sanitise",
        json={
            "documents": [{"id": "payslip", "text": payslip_text}],
            "spans": {
                "payslip": [
                    {"id": "name-1", "type": "name", "start": 25, "end": 34, "value": "A. Okafor"}
                ]
            },
            "toggles": {"name": "blacklabel"},
            "passphrase": None,
        },
    )
    assert response.status_code == 200
    payload = response.json()["sanitised_payload"]
    assert "A. Okafor" not in payload
    assert "█" in payload


def test_post_sanitise_missing_toggles_returns_400(api_client, payslip_text):
    response = api_client.post(
        "/api/sanitise",
        json={"documents": [{"id": "payslip", "text": payslip_text}], "spans": {}},
    )
    assert response.status_code == 400


def test_post_sanitise_unknown_doc_id_in_spans_returns_422(api_client, payslip_text):
    response = api_client.post(
        "/api/sanitise",
        json={
            "documents": [{"id": "payslip", "text": payslip_text}],
            "spans": {"unknown_doc": []},
            "toggles": {"name": "blacklabel"},
        },
    )
    assert response.status_code == 422


def test_post_sanitise_all_blacklabeled_returns_fully_redacted(api_client):
    """FR-26: if all types are blacklabeled, sanitised payload is fully redacted but still returned."""
    response = api_client.post(
        "/api/sanitise",
        json={
            "documents": [{"id": "payslip", "text": "Name: Alice\nPhone: 07700 900123"}],
            "spans": {
                "payslip": [
                    {"id": "n1", "type": "name", "start": 6, "end": 11, "value": "Alice"},
                    {"id": "p1", "type": "phone", "start": 19, "end": 31, "value": "07700 900123"},
                ]
            },
            "toggles": {"name": "blacklabel", "phone": "blacklabel"},
            "passphrase": None,
        },
    )
    assert response.status_code == 200
    payload = response.json()["sanitised_payload"]
    assert "Alice" not in payload
    assert "07700 900123" not in payload


# --- /api/reason ---------------------------------------------------------


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


# --- /api/audit ---------------------------------------------------------


def test_post_audit_returns_entries(api_client):
    """POST /api/audit returns audit log."""
    response = api_client.post(
        "/api/audit",
        json={
            "spans": {"payslip": [{"id": "n1", "type": "name", "start": 0, "end": 5, "value": "Alice"}]},
            "toggles": {"name": "blacklabel"},
            "detection_results": {
                "payslip": {"spans": [], "fallback_triggered": False, "warning": ""}
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "audit_log" in data
    assert len(data["audit_log"]) >= 1


def test_post_audit_includes_fallback_entry(api_client):
    response = api_client.post(
        "/api/audit",
        json={
            "spans": {"payslip": [{"id": "n1", "type": "name", "start": 0, "end": 5, "value": "Alice"}]},
            "toggles": {"name": "keep"},
            "detection_results": {
                "payslip": {"spans": [], "fallback_triggered": True, "warning": "Local model unavailable"}
            },
        },
    )
    assert response.status_code == 200
    audit_log = response.json()["audit_log"]
    assert any(e["decision"] == "fallback" for e in audit_log)


# --- static / PWA routes ---------------------------------------------------


def test_get_root_redirects_to_vault(api_client):
    """GET / redirects to /vault/ (multi-page, not SPA)."""
    response = api_client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert "/vault" in response.headers.get("location", "")


def test_get_manifest_json(api_client):
    """GET /manifest.json serves PWA manifest."""
    response = api_client.get("/manifest.json")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Privacy Gate"
    assert "icons" in data


def test_get_favicon(api_client):
    response = api_client.get("/favicon.ico")
    assert response.status_code == 200
    assert "image" in response.headers.get("content-type", "")


def test_post_extract_pdf(api_client):
    import base64

    from app.test_extract_pdf import pdf_with_text

    raw = pdf_with_text("Payslip for A. Okafor")
    response = api_client.post(
        "/api/extract",
        json={"filename": "payslip.pdf", "bytes_b64": base64.b64encode(raw).decode("ascii")},
    )
    assert response.status_code == 200
    assert "Okafor" in response.json()["text"]


def test_transfer_round_trip(api_client):
    posted = api_client.post(
        "/api/transfer",
        json={"name": "July payslip", "text": "sanitised copy", "perm": "download", "ttl": 3600},
    )
    assert posted.status_code == 200
    tid = posted.json()["id"]
    assert tid
    got = api_client.get("/api/transfer/" + tid)
    assert got.status_code == 200
    body = got.json()
    assert body["name"] == "July payslip"
    assert body["text"] == "sanitised copy"
    assert body["perm"] == "download"


def test_transfer_missing_is_404(api_client):
    response = api_client.get("/api/transfer/not-a-real-id")
    assert response.status_code == 404
