"""POST /api/reason: cloud reasoning step over the text the user approved.

Calls Gemini 3.7 Flash via the google-genai SDK (client.interactions.create,
the same surface as starter/02_tool_agent.py and app/pipeline.py). This step
is optional to the product: the local redaction step is the whole value,
this is a thing the user chooses to do with what they approved to share.

Never fabricates a finding: if there is no API key, or the call fails, or
the model's reply cannot be parsed as the expected JSON, this returns an
error dict instead of inventing content. The server maps that to HTTP 503.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from starter.utils import DEFAULT_MODEL, with_retry  # noqa: E402

_PROMPT_INSTRUCTION = (
    "You are helping someone who has just reviewed and approved sharing a "
    "document (personal details already removed by them). Read the text "
    "below and reply with ONLY a JSON object, no other words: "
    '{"finding": "<one short sentence, what the document is about or what '
    'matters in it>", "explanation": "<1-2 sentences on why that matters>", '
    '"draft": "<a short draft reply or next step based on the document>"}.\n\n'
    "TEXT:\n"
)


def _has_key() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


@with_retry(max_attempts=2)
def _call(client, prompt: str):
    return client.interactions.create(model=DEFAULT_MODEL, store=False, input=prompt)


def reason(text: str) -> dict:
    """Returns either {"finding","explanation","draft","model"} or
    {"error": "..."} on any failure. Never guesses at content."""
    if not _has_key():
        return {"error": "no Gemini API key configured (GEMINI_API_KEY / GOOGLE_API_KEY)"}

    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    try:
        client = genai.Client(api_key=api_key)
        resp = _call(client, _PROMPT_INSTRUCTION + text)
    except Exception as e:
        return {"error": f"Gemini call failed: {e}"}

    output_text = getattr(resp, "output_text", None) or ""
    data = _extract_json(output_text)
    finding = str(data.get("finding") or "").strip()
    explanation = str(data.get("explanation") or "").strip()
    draft = str(data.get("draft") or "").strip()
    if not finding:
        return {"error": "model reply did not contain a usable finding"}

    return {
        "finding": finding,
        "explanation": explanation,
        "draft": draft,
        "model": DEFAULT_MODEL,
    }
