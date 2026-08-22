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

# gemini-3.7-flash is the current GA model as of Aug 2026 — it supersedes
# gemini-3-pro-preview and gemini-3.1-flash-lite-preview, both now shut down
# per ai.google.dev/gemini-api/docs/models. Override with GEMINI_MODEL if
# it's been retired by the time you read this — see that page for the
# current list. Supports thinking_level "low"/"medium"/"high" (default
# medium) if you want to trade latency for reasoning quality.
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
    """Print token usage from a legacy generate_content response.usage_metadata.
    Kept for the commented legacy fallback blocks in each script."""
    if usage_metadata is None:
        print("  (no usage metadata returned)")
        return
    prompt = getattr(usage_metadata, "prompt_token_count", None)
    output = getattr(usage_metadata, "candidates_token_count", None)
    total = getattr(usage_metadata, "total_token_count", None)
    print(f"  tokens -> prompt: {prompt} | output: {output} | total: {total}")


def print_interaction_usage(usages):
    """Print total token usage from the Interactions API's response.usage.

    Accepts a single usage object or a list of them (an agent loop that makes
    several interactions.create round trips can pass the whole list to get a
    running total). `total_input_tokens` is confirmed against
    docs/tokens.md; `total_output_tokens` is inferred by naming symmetry and
    read defensively via getattr so a name change won't crash the demo.
    """
    if usages is None:
        print("  (no usage metadata returned)")
        return
    if not isinstance(usages, (list, tuple)):
        usages = [usages]
    usages = [u for u in usages if u is not None]
    if not usages:
        print("  (no usage metadata returned)")
        return
    input_total = sum(getattr(u, "total_input_tokens", 0) or 0 for u in usages)
    output_total = sum(getattr(u, "total_output_tokens", 0) or 0 for u in usages)
    print(f"  tokens -> input: {input_total} | output: {output_total} (across {len(usages)} call(s))")
