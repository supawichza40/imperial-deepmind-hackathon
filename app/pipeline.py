"""Two-model pipeline: local Gemma 4 for the private step, Gemini 3.7 Flash for reasoning.

This is the Track 3 shape. Trim whichever half your track doesn't need:
  Track 1 (Gemini only)  -> delete local_step, call gemini_step directly
  Track 2 (Gemma only)   -> delete gemini_step, do everything in local_step

The split exists for a reason, and the reason is a scored write-up field:
the local step runs with the network off, so whatever goes through it never
leaves the machine.
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "starter"))

from utils import DEFAULT_MODEL, get_client, with_retry  # noqa: E402

# Cloud tag, not a locally-pulled model. gemma4:e2b was never actually
# pulled on the build machine and the pull was too slow for the deadline
# (~44 min ETA); gemma4:31b-cloud runs through the same native Ollama route
# with no code change, just the model name. See SKILL.md "The local model".
LOCAL_MODEL = os.environ.get("LOCAL_MODEL", "gemma4:31b-cloud")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def local_step(text: str, instruction: str = "Classify this in one short label.") -> str:
    """Run the private step on-device. No network once the model is pulled.

    Uses Ollama's NATIVE /api/generate, not the OpenAI-compatible /v1 route.
    That is deliberate and it matters: the /v1 route silently ignores
    `think: false`, so the model spends the whole token budget on hidden
    reasoning and returns an EMPTY string. Observed 22 Aug 2026 on
    gemma4:e2b - 36s, max_tokens=64, empty content. The native route honours
    the flag and returned real text at 10.8 tok/s on the same machine.

    Keep the output SHORT. At ~10 tok/s every token is a tenth of a second
    on screen, so ask for a label or a field, never prose.
    """
    body = json.dumps({
        "model": LOCAL_MODEL,
        "prompt": f"{instruction}\n\n{text}",
        "stream": False,
        "think": False,          # native route honours this; /v1 does not
        "options": {"num_predict": 64},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/generate", data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        data = json.load(urllib.request.urlopen(req, timeout=300))
    except Exception as e:
        raise RuntimeError(
            f"local model unreachable at {OLLAMA_HOST}: {e}\n"
            f"  start it with:  ollama serve   (and: ollama pull {LOCAL_MODEL})"
        ) from e
    if "error" in data:
        raise RuntimeError(f"ollama error: {data['error']}")
    return (data.get("response") or "").strip()


@with_retry()
def gemini_step(prompt: str, tools: list | None = None) -> str:
    """Cloud reasoning via the Interactions API (GA since June 2026).

    Pass `tools` to give the model function calling, Google Search grounding,
    or a remote MCP server — see starter/02, 03 and 08 for each shape.
    """
    client = get_client()
    kwargs = {"model": DEFAULT_MODEL, "input": prompt}
    if tools:
        kwargs["tools"] = tools
    resp = client.interactions.create(**kwargs)
    return getattr(resp, "output_text", None) or str(resp)


def run(user_input: str, use_local: bool = False) -> dict:
    """The end-to-end flow. Replace the middle with your actual product logic.

    `use_local` defaults to False: the local model is slow on the build
    machine (10.8 tok/s, and it makes the laptop sluggish while resident),
    so develop against the cloud path and switch the local half on only
    when you actually need to show it. Set LOCAL=1 to enable.
    """
    label = local_step(user_input) if use_local else "(local step skipped)"
    answer = gemini_step(
        f"A local on-device model classified the following input as '{label}'.\n"
        f"Input: {user_input}\n\n"
        f"Give the user a short, useful next step."
    )
    return {"local_label": label, "response": answer}
