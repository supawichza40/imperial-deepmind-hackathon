"""Gemini reasoning step — detects inconsistencies in sanitised documents.

Uses Gemini 3.7 Flash via the Interactions API to analyze a sanitised payload
and return a structured JSON result: {inconsistency_detected, analysis, draft_letter}.

Privacy note: reasoner.py only receives the sanitised payload (no original text).
The backend ensures this by calling sanitiser first.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

from utils import DEFAULT_MODEL, get_client, with_retry  # noqa: E402
from app.types import GeminiResult  # noqa: E402


def _strip_json_fences(text: str) -> str:
    """Strip markdown ```json ... ``` wrappers before JSON parsing.

    Gemini sometimes wraps JSON in code fences. This defensively removes them
    before attempting json.loads().
    """
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].lstrip("\n")
    if text.endswith("```"):
        text = text[:-3].rstrip()
    return text


@with_retry(max_attempts=5, base_delay=1.5)
def _call_gemini(prompt: str) -> str:
    """Call Gemini 3.7 Flash via the Interactions API.

    Wrapped in with_retry() to handle transient failures (429, 503).
    Returns the raw output_text from the response.
    """
    client = get_client()
    resp = client.interactions.create(
        model=DEFAULT_MODEL,
        input=prompt,
    )
    return getattr(resp, "output_text", None) or str(resp)


def reason(sanitised_payload: str, instruction: str = None) -> GeminiResult:
    """Analyse a sanitised payload for inconsistencies.

    Takes the redacted (sanitised) text and asks Gemini to:
    1. Detect inconsistencies in the visible fields
    2. Provide a detailed analysis
    3. Draft a follow-up letter if inconsistencies are found

    Returns a GeminiResult dict: {inconsistency_detected, analysis, draft_letter}

    On any failure (after retries), returns a safe fallback:
    {inconsistency_detected: False, analysis: "Cloud check unavailable", draft_letter: ""}

    Args:
        sanitised_payload: The redacted document text (█ bars + [ENCRYPTED] tokens)
        instruction: Optional custom instruction (defaults to a standard prompt)

    Returns:
        GeminiResult: {inconsistency_detected, analysis, draft_letter}
    """
    if instruction is None:
        instruction = (
            "You are analyzing a redacted financial document. "
            "Some fields are marked with █ or [ENCRYPTED] and should be ignored in your analysis. "
            "Analyze only the visible fields for internal inconsistencies (e.g. mismatch between gross pay and net pay, "
            "incompatible employment dates, etc). "
            "Respond with a JSON object: "
            '{"inconsistency_detected": boolean, "analysis": "your detailed findings", "draft_letter": "a brief follow-up if inconsistencies found, or empty string"}'
        )

    prompt = f"{instruction}\n\nDocument to analyze:\n\n{sanitised_payload}"

    try:
        # Call Gemini via the Interactions API (with automatic retry on 429/503)
        raw_response = _call_gemini(prompt)

        # Defensively strip markdown code fences if present
        cleaned = _strip_json_fences(raw_response)

        # Parse the JSON
        result = json.loads(cleaned)

        # Validate the required fields exist
        if not all(k in result for k in ["inconsistency_detected", "analysis", "draft_letter"]):
            # Missing field — return safe fallback
            return {
                "inconsistency_detected": False,
                "analysis": "Cloud check returned incomplete response",
                "draft_letter": "",
            }

        return {
            "inconsistency_detected": bool(result["inconsistency_detected"]),
            "analysis": str(result["analysis"]),
            "draft_letter": str(result["draft_letter"]),
        }

    except json.JSONDecodeError:
        # Unparseable JSON — return safe fallback
        return {
            "inconsistency_detected": False,
            "analysis": "Cloud check returned non-JSON response",
            "draft_letter": "",
        }

    except Exception as e:
        # Any other error (network timeout after retries, API error, etc.)
        # Return a safe fallback instead of raising
        return {
            "inconsistency_detected": False,
            "analysis": f"Cloud check could not complete: {type(e).__name__}",
            "draft_letter": "",
        }
