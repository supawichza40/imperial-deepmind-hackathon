# Gemini agent starter kit

Go from `git clone` to a working Gemini agent in under 10 minutes. Built for
the UK AI Agent Lab: Gemini Edition hackathon (Google DeepMind, London).

## What's in here

| File | What it shows |
|---|---|
| `01_hello_gemini.py` | The simplest possible call: prompt in, text + token usage out. |
| `02_tool_agent.py` | Automatic function calling — 3 tools, multi-step reasoning, printed live. |
| `03_grounded_agent.py` | Google Search grounding + URL context, with citations. |
| `04_structured_output.py` | JSON extraction into a typed Pydantic object. |
| `05_multi_agent.py` | Orchestrator + 2 specialist sub-agents, plain SDK calls (no framework). |
| `06_live_voice_agent.py` | Live API realtime session skeleton (text by default, notes for audio). |
| `07_local_gemma.py` | Offline fallback: local Gemma via Ollama, same call shape as OpenAI. |
| `utils.py` | Shared client factory, retry-with-backoff, pretty tool-call printer. |
| `demo_fallback.md` | Checklist for a demo that can't die on stage. |

## Setup (macOS, zsh) — under 10 minutes

```zsh
cd starter

# 1. Virtual env
python3 -m venv .venv
source .venv/bin/activate

# 2. Install deps
pip install -r requirements.txt

# 3. Get a free API key
open https://aistudio.google.com/apikey

# 4. Configure your key
cp .env.example .env
# then edit .env and paste your key in as GEMINI_API_KEY=...

# 5. Run the simplest demo
python 01_hello_gemini.py
```

If that prints a sentence and a token count, you're set — every other
`0X_*.py` script runs the same way.

## Running the rest

```zsh
python 02_tool_agent.py          # watch it call 3 tools in sequence
python 03_grounded_agent.py      # live web search + citations
python 04_structured_output.py   # typed JSON extraction
python 05_multi_agent.py         # orchestrator + 2 specialists
python 06_live_voice_agent.py    # realtime session skeleton (no mic needed)
python 07_local_gemma.py         # OFFLINE fallback — needs Ollama, see file header
```

## Model

All scripts default to `gemini-3.7-flash` (fast + cheap, good for a hack).
Override it without touching code:

```zsh
export GEMINI_MODEL=gemini-3-pro-preview   # or whatever's current —
# see https://ai.google.dev/gemini-api/docs/models for the live list
```

## If something breaks mid-demo

Read `demo_fallback.md` before you're on stage, not during it. Short version:
`utils.py` already retries 429/503 with backoff, and `07_local_gemma.py` is
your no-wifi-needed escape hatch — pull the model early while wifi is good:

```zsh
brew install ollama
ollama pull gemma3:4b
```

## Notes on the SDK

This kit uses `google-genai` (`from google import genai`), Google's current
Python SDK — not the older, deprecated `google-generativeai` package. Two
call shapes exist side by side right now, and you'll see both in Google's
own docs depending on the page:

- `client.models.generate_content(...)` — the original, most-documented call
  shape. Used in `01`, `02`, `05`.
- `client.interactions.create(...)` — Google's newer unified interface for
  models and agents (GA since mid-2026), with cleaner grounding citations
  and schema-based structured output. Used in `03`, `04`.

Both are real, current, and supported.
