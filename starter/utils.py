"""Shared helpers for the Gemini hackathon starter kit.

Import whatever you need from any 0X_*.py script:
    from utils import get_client, DEFAULT_MODEL, with_retry, print_tool_call
"""
import functools
import os
import sys
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

# Docs across ai.google.dev (quickstart, function-calling, structured-output,
# grounding, url-context) all use this model name as of Aug 2026. Override
# with GEMINI_MODEL if it's been retired by the time you read this — see
# https://ai.google.dev/gemini-api/docs/models for the current list.
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")

# Verified against the Live API capabilities guide (docs/live-guide).
LIVE_MODEL = os.environ.get("GEMINI_LIVE_MODEL", "gemini-3.1-flash-live-preview")


def get_client() -> genai.Client:
    """Build a Gemini client from the API key in the environment.

    Reads GEMINI_API_KEY (preferred) or GOOGLE_API_KEY. Exits with a plain
    human-readable message instead of a stack trace if neither is set —
    the last thing you want mid-demo is your teammate staring at a traceback.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        sys.exit(
            "\n[setup error] No Gemini API key found.\n"
            "  1. Get a free key:  https://aistudio.google.com/apikey\n"
            "  2. Copy the template: cp .env.example .env\n"
            "  3. Paste your key into .env as GEMINI_API_KEY=...\n"
        )
    return genai.Client(api_key=api_key)


_RETRYABLE_HTTP_CODES = {429, 500, 503}
_RETRYABLE_MARKERS = ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")


def with_retry(max_attempts: int = 5, base_delay: float = 1.5):
    """Retry decorator with exponential backoff for rate limits (429) and
    transient server errors (500/503) — the two failure modes most likely to
    hit a demo mid-pitch on a shared free-tier key.

    Catches a broad Exception on purpose: the SDK's own error classes
    (google.genai.errors.ClientError / ServerError) aren't guaranteed stable
    across versions, so this checks the HTTP status via `.code` first and
    falls back to sniffing the error text for the same signal.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    code = getattr(e, "code", None)
                    text = str(e)
                    retryable = code in _RETRYABLE_HTTP_CODES or any(
                        marker in text for marker in _RETRYABLE_MARKERS
                    )
                    if not retryable or attempt == max_attempts:
                        raise
                    print(
                        f"  [retry] {type(e).__name__} (attempt {attempt}/{max_attempts}) "
                        f"— backing off {delay:.1f}s ..."
                    )
                    time.sleep(delay)
                    delay *= 2
        return wrapper
    return decorator


def print_header(title: str):
    bar = "=" * len(title)
    print(f"\n{bar}\n{title}\n{bar}")


def print_tool_call(name: str, args: dict, result=None):
    """Pretty-print a tool invocation so a demo audience can watch the agent
    reason and act, not just see the final answer appear."""
    arg_str = ", ".join(f"{k}={v!r}" for k, v in args.items())
    print(f"  \U0001f527 tool call: {name}({arg_str})")
    if result is not None:
        print(f"     -> {result}")


def print_usage(usage_metadata):
    """Print token usage from a classic generate_content response.usage_metadata."""
    if usage_metadata is None:
        print("  (no usage metadata returned)")
        return
    prompt = getattr(usage_metadata, "prompt_token_count", None)
    output = getattr(usage_metadata, "candidates_token_count", None)
    total = getattr(usage_metadata, "total_token_count", None)
    print(f"  tokens -> prompt: {prompt} | output: {output} | total: {total}")
