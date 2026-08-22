"""Shared pytest fixtures for Privacy Gate tests.

See docs/specs/testing.md §2.1 — this file mirrors that spec verbatim.
"""

import json
import urllib.error

import pytest
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
    # Local import: app/api/main.py may not exist yet while other agents are
    # still building it. Importing here (instead of at module scope) keeps
    # test collection working for every test file that doesn't need it.
    from fastapi.testclient import TestClient
    from app.api.main import app

    return TestClient(app)


@pytest.fixture
def mock_ollama_success():
    """Mock Ollama returning valid JSON spans."""
    mock_response = {
        "response": '[{"text": "A. Okafor", "type": "name"}, {"text": "14 Pelham St, SW7", "type": "address"}]'
    }
    with patch("app.detector.urllib.request.urlopen") as mock:
        mock.return_value = MagicMock()
        mock.return_value.read.return_value = json.dumps(mock_response).encode()
        yield mock


@pytest.fixture
def mock_ollama_timeout():
    """Mock Ollama timing out — triggers regex-only fallback."""
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


@pytest.fixture
def mock_gemini_with_fences():
    """Mock Gemini returning JSON wrapped in markdown code fences."""
    with patch("app.reasoner.get_client") as mock:
        client = MagicMock()
        resp = MagicMock()
        resp.output_text = '```json\n{"inconsistency_detected": false, "analysis": "All good", "draft_letter": ""}\n```'
        client.interactions.create.return_value = resp
        mock.return_value = client
        yield mock
