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
| `08_remote_mcp.py` | Native remote MCP tool — no local MCP client needed. |
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
python 08_remote_mcp.py          # remote MCP tool call, zero local MCP client
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
Python SDK — not the older, deprecated `google-generativeai` package.

Every script (`01`–`05`) defaults to the **Interactions API**
(`client.interactions.create(...)`) — Google's current, recommended surface
for models *and* agents, GA since June 2026. Straight from
[ai.google.dev/gemini-api/docs/interactions](https://ai.google.dev/gemini-api/docs/interactions):

> "The Interactions API is the best way to build with Gemini models and
> agents. As of June 2026, it is Generally Available and recommended for
> all new projects. While it is now considered legacy, the original
> `generateContent` API remains fully supported."

Each script has a **commented legacy fallback block** at the bottom using
`client.models.generate_content(...)` — uncomment it if the venue wifi's
`pip install` pulls an older `google-genai` version that predates
`client.interactions`. One real capability gap to know about: legacy
`generateContent` supports *automatic* function calling (pass raw Python
functions, the SDK loops for you); the Interactions API doesn't do that yet,
so `02_tool_agent.py` drives its own function-call ↔ function-result loop
by hand (see `run_agent()` in that file) — still fully automatic from the
user's point of view, just a few more lines of code.

`06_live_voice_agent.py` (Live API) and `07_local_gemma.py` (Ollama) are
separate surfaces, unaffected by this choice.

`08_remote_mcp.py` uses the Interactions API's native `mcp_server` tool —
give it a URL (and optional auth headers), Gemini handles the whole MCP
handshake server-side, no local MCP client needed. It defaults to
[DeepWiki's public MCP server](https://mcp.deepwiki.com/mcp) (free, no auth)
so it runs with zero extra setup.

As of 21 Jul 2026, `temperature`/`top_p`/`top_k` are deprecated in favor of
`thinking_level` (`"low"`/`"medium"`/`"high"`, default medium for
`gemini-3.7-flash`; `"minimal"` isn't accepted on every model). None of
these scripts set sampling params, so there's nothing to migrate — just
don't reach for the old ones if you extend this kit.
