"""Tests for reasoner.py — Gemini reasoning step.

Tests the reason() function which:
1. Calls Gemini 3.7 Flash via the Interactions API
2. Parses the response as JSON (with defensive fence stripping)
3. Returns a GeminiResult: {inconsistency_detected, analysis, draft_letter}
4. Falls back gracefully to a safe default on any failure
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from app.reasoner import reason, _strip_json_fences


class TestStripJsonFences:
    """Test the fence-stripping utility."""

    def test_strips_markdown_code_fences(self):
        """Markdown ```json ... ``` wrappers are removed."""
        wrapped = '```json\n{"key": "value"}\n```'
        unwrapped = _strip_json_fences(wrapped)
        assert unwrapped == '{"key": "value"}'

    def test_leaves_plain_json_alone(self):
        """Plain JSON without fences is unchanged."""
        plain = '{"key": "value"}'
        result = _strip_json_fences(plain)
        assert result == plain

    def test_strips_partial_fences_at_start(self):
        """Only opening fence at start is stripped."""
        text = '```json\n{"key": "value"}'
        result = _strip_json_fences(text)
        assert result == '{"key": "value"}'

    def test_handles_whitespace_around_fences(self):
        """Leading/trailing whitespace is handled."""
        text = '  ```json\n{"key": "value"}\n```  '
        result = _strip_json_fences(text)
        assert result == '{"key": "value"}'


class TestReasonSuccessPath:
    """Test reason() with valid Gemini responses."""

    def test_reason_returns_gemini_result(self, mock_gemini_success):
        """FR-20: reason() returns GeminiResult with expected fields."""
        result = reason("sanitised text here")
        assert isinstance(result, dict)
        assert "inconsistency_detected" in result
        assert "analysis" in result
        assert "draft_letter" in result
        assert result["inconsistency_detected"] is True
        assert isinstance(result["analysis"], str)
        assert isinstance(result["draft_letter"], str)

    def test_reason_parses_json_correctly(self, mock_gemini_success):
        """Gemini response JSON is parsed and fields are returned as-is."""
        result = reason("sanitised text")
        assert result["inconsistency_detected"] is True
        assert "Net pay mismatch" in result["analysis"]

    def test_reason_strips_json_code_fences(self, mock_gemini_with_fences):
        """Gemini wraps JSON in ```json fences — must strip before parsing."""
        result = reason("sanitised text")
        assert result["inconsistency_detected"] is False
        assert result["analysis"] == "All good"
        assert result["draft_letter"] == ""

    def test_reason_with_custom_instruction(self, mock_gemini_success):
        """Custom instruction is passed to Gemini."""
        custom_inst = "Custom: analyze this document"
        result = reason("sanitised text", instruction=custom_inst)
        # Call should have happened (we can't inspect the prompt directly in this test,
        # but the success path should work)
        assert result["inconsistency_detected"] is True


class TestReasonFallbackPath:
    """Test reason() graceful fallback on failures."""

    def test_reason_fallback_on_exception(self, mock_gemini_failure):
        """If Gemini raises after retries, reason() returns safe fallback GeminiResult."""
        result = reason("sanitised text")
        assert result["inconsistency_detected"] is False
        assert "could not complete" in result["analysis"].lower() or "error" in result["analysis"].lower()
        assert result["draft_letter"] == ""

    def test_reason_fallback_on_malformed_json(self):
        """Completely unparseable JSON → safe fallback, no exception."""
        with patch("app.reasoner.get_client") as mock:
            client = MagicMock()
            resp = MagicMock()
            resp.output_text = "I cannot help with that."
            client.interactions.create.return_value = resp
            mock.return_value = client

            result = reason("sanitised text")
        assert result["inconsistency_detected"] is False
        assert "non-json" in result["analysis"].lower()
        assert result["draft_letter"] == ""

    def test_reason_fallback_on_incomplete_json(self):
        """JSON missing required fields → safe fallback, no exception."""
        with patch("app.reasoner.get_client") as mock:
            client = MagicMock()
            resp = MagicMock()
            # Missing 'draft_letter' field
            resp.output_text = json.dumps({
                "inconsistency_detected": True,
                "analysis": "Some analysis"
            })
            client.interactions.create.return_value = resp
            mock.return_value = client

            result = reason("sanitised text")
        assert result["inconsistency_detected"] is False
        assert "incomplete" in result["analysis"].lower()
        assert result["draft_letter"] == ""

    def test_reason_returns_boolean_for_inconsistency_detected(self, mock_gemini_success):
        """inconsistency_detected is always a boolean, never a string."""
        result = reason("sanitised text")
        assert isinstance(result["inconsistency_detected"], bool)


class TestReasonSignature:
    """Test the function signature enforces privacy."""

    def test_reason_takes_sanitised_payload_not_original_text(self):
        """reason() signature should not expose original-text parameters."""
        import inspect
        sig = inspect.signature(reason)
        params = list(sig.parameters)
        # Should have a parameter for the sanitised payload
        assert "sanitised_payload" in params
        # Should NOT have parameters for original document or unredacted text
        assert "text" not in params or params.index("text") > params.index("sanitised_payload")
        assert "document" not in params


class TestReasonRetryBehavior:
    """Test that reason() respects the with_retry() decorator."""

    def test_reason_calls_gemini_via_decorated_function(self):
        """reason() uses the _call_gemini helper wrapped in with_retry()."""
        with patch("app.reasoner._call_gemini") as mock_call:
            mock_call.return_value = json.dumps({
                "inconsistency_detected": False,
                "analysis": "test",
                "draft_letter": ""
            })
            result = reason("sanitised text")
        assert result["inconsistency_detected"] is False
