"""End-to-end test: the full documented flow through the real API.

detect -> user approves consent -> sanitise -> reason -> audit
(architecture.md §4.2, development-plan.md F4.1).

Ollama and Gemini are mocked at the same seams the unit tests use
(app.detector.urllib.request.urlopen, app.reasoner.get_client) so this
runs offline and fast, but every other layer -- FastAPI routing, Pydantic
validation, detector regex+merge, sanitiser reverse-offset redaction,
audit build -- is exercised for real, wired together exactly as the
frontend would call it.
"""
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.fixtures import DOCUMENTS

client = TestClient(app)


@pytest.fixture
def mock_ollama_no_gemma():
    """Force regex-only detection so the e2e test doesn't depend on Gemma's
    free-text extraction quality -- only on the deterministic regex layer,
    the API wiring, and the sanitise/audit steps built on top of it."""
    import urllib.error

    with patch(
        "app.detector.urllib.request.urlopen", side_effect=urllib.error.URLError("no ollama in ci")
    ):
        yield


@pytest.fixture
def mock_gemini():
    with patch("app.reasoner.get_client") as mock:
        client_mock = MagicMock()
        resp = MagicMock()
        resp.output_text = json.dumps(
            {
                "inconsistency_detected": True,
                "analysis": "Net pay does not match the deposit amount.",
                "draft_letter": "Dear HR, please clarify the £52.60 difference.",
            }
        )
        client_mock.interactions.create.return_value = resp
        mock.return_value = client_mock
        yield mock


def test_full_pipeline_detect_sanitise_reason_audit(mock_ollama_no_gemma, mock_gemini):
    payslip_text = DOCUMENTS["payslip"]

    # 1. Detect
    detect_resp = client.post(
        "/api/detect",
        json={"documents": [{"id": "payslip", "text": payslip_text}]},
    )
    assert detect_resp.status_code == 200
    detection = detect_resp.json()["results"]["payslip"]
    assert detection["fallback_triggered"] is True  # Ollama was mocked to fail
    assert len(detection["spans"]) > 0
    ni_spans = [s for s in detection["spans"] if s["type"] == "ni_number"]
    assert len(ni_spans) == 1

    # 2. User approves consent: blacklabel identity fields, keep everything else.
    toggles = {"ni_number": "blacklabel", "account_number": "blacklabel", "name": "blacklabel"}

    # 3. Sanitise
    sanitise_resp = client.post(
        "/api/sanitise",
        json={
            "documents": [{"id": "payslip", "text": payslip_text}],
            "spans": {"payslip": detection["spans"]},
            "toggles": toggles,
        },
    )
    assert sanitise_resp.status_code == 200
    sanitised_payload = sanitise_resp.json()["sanitised_payload"]
    assert "QQ123456C" not in sanitised_payload  # NI number redacted
    assert "█" in sanitised_payload

    # 4. Reason over the sanitised payload only -- Gemini never sees the original.
    reason_resp = client.post("/api/reason", json={"sanitised_payload": sanitised_payload})
    assert reason_resp.status_code == 200
    reasoning = reason_resp.json()
    assert reasoning["inconsistency_detected"] is True
    assert "analysis" in reasoning

    call_kwargs = mock_gemini.return_value.interactions.create.call_args.kwargs
    sent_to_gemini = call_kwargs.get("input", "")
    assert "QQ123456C" not in sent_to_gemini

    # 5. Audit trail records what stayed local and what was fallback.
    audit_resp = client.post(
        "/api/audit",
        json={
            "spans": {"payslip": detection["spans"]},
            "toggles": toggles,
            "detection_results": {"payslip": detection},
        },
    )
    assert audit_resp.status_code == 200
    audit_log = audit_resp.json()["audit_log"]
    assert any(e["decision"] == "fallback" for e in audit_log)
    assert any(e["field_type"] == "ni_number" and e["decision"] == "kept_local" for e in audit_log)


def test_documents_endpoint_lists_fixtures():
    resp = client.get("/api/documents")
    assert resp.status_code == 200
    ids = {d["id"] for d in resp.json()["documents"]}
    assert "payslip" in ids
    assert "bank_statement" in ids
