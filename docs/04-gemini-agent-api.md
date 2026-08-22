# Gemini API — Agent-Building Reference (Aug 2026)

Everything you can wire up in a 5-hour hackathon window, using the `google-genai` SDK
(Python/JS). Every claim below links to the doc page it came from. Anything I could not
confirm from an official source is marked **UNVERIFIED**.

`pip install google-genai` / `npm install @google/genai`. Get a key at
[aistudio.google.com](https://aistudio.google.com), set `GEMINI_API_KEY`.

---

## 0. What to build if you have 5 hours

| If your demo needs... | Use this | Why it's fast to wire up |
|---|---|---|
| A voice/video agent people talk to live | **Live API** (`gemini-3.1-flash-live-preview`) | One websocket session, built-in VAD + interruption, biggest "wow" per hour invested — [source](https://ai.google.dev/gemini-api/docs/live) |
| An agent that browses the web / clicks buttons for the user | **Computer Use tool** (`gemini-2.5-computer-use-preview-10-2025`, or built into `gemini-3-flash-preview`) + Playwright — ⚠️ **Preview status, see [§7](#7-computer-use)** | Screenshot → model returns a click/type action → you execute it — [source](https://ai.google.dev/gemini-api/docs/computer-use) |
| An agent that answers with live facts / current events | **`google_search` built-in tool** | Zero infra — one line in `tools=[]`, no scraping needed — [source](https://ai.google.dev/gemini-api/docs/grounding) |
| An agent that calls your own backend/APIs | **Function calling**, Interactions API (`tools=[...]`) | Declare a JSON-schema function, get a `function_call` step back — [source](https://ai.google.dev/gemini-api/docs/function-calling) |
| An agent that must emit clean JSON for your frontend | **`response_format`** structured output | Pass a Pydantic model, get validated JSON back, combine with tools — [source](https://ai.google.dev/gemini-api/docs/structured-output) |
| An agent that plugs into an existing MCP tool server | **Remote MCP** as a native Interactions API tool type | Point `tools=[{"type": "mcp_server", "url": "..."}]` at any Streamable-HTTP MCP server — no client code at all, see [§5](#5-mcp-model-context-protocol-support) — [source](https://ai.google.dev/gemini-api/docs/function-calling) |
| A full autonomous agent, zero orchestration code | **Managed agents** (Deep Research / Antigravity) | Same `client.interactions.create()` call, just swap `model=` — see [§1.1](#11-managed-agents--call-googles-own-agents-directly) |
| A long batch job (scoring, data-prep) that isn't part of the live demo | **Batch API** | 50% cheaper, fire-and-forget, doesn't burn your rate limit during the demo — [source](https://ai.google.dev/gemini-api/docs/batch-mode) |

Default model choice for everything else: **`gemini-3.7-flash`** — GA (not preview) as
of **13 Aug 2026**, Google's own description is "most intelligent workhorse model yet
for coding and agents." It's fast, has function calling + all built-in tools +
structured output in one model, and — unlike the `-preview` models — isn't at risk of
being pulled or rate-limited harder right before your demo.
[Source](https://ai.google.dev/gemini-api/docs/changelog) (Aug 13 2026 entry),
[model page](https://ai.google.dev/gemini-api/docs/latest-model). Computer use is
still only on preview/specialized models — see [§7](#7-computer-use).

---

## 1. Two API surfaces — pick one before you start

As of June 2026 Google ships **two** parallel calling conventions. Mixing them mid-build
wastes time, so decide up front.

| | **Interactions API** (`client.interactions.create(...)`) | **generateContent API** (`client.models.generate_content(...)`) |
|---|---|---|
| Status | GA since June 2026, "primary interface for Gemini models and agents" | Legacy but fully supported; still gets new mainline models |
| Endpoint | `POST https://generativelanguage.googleapis.com/v1beta/interactions` | `POST .../v1beta/models/{model}:generateContent` |
| Best for | Agentic workflows, multi-turn state, tool orchestration, anything new | Stable production paths; features Interactions doesn't have yet |
| Multi-turn memory | Built-in server-side via `previous_interaction_id` (`store=true` by default) | You resend full `contents` history yourself, or use `client.chats.create()` |
| Missing today | Explicit context caching, custom safety-setting thresholds, video metadata (all **only on generateContent**) | — |
| MCP client support | **Confirmed, current, and the easier path**: native `mcp_server` remote-tool type — see [§5](#5-mcp-model-context-protocol-support) | Also confirmed, via local `ClientSession` object passed into `tools=[...]` |
| Data retention | Interactions stored by default (`store=true`): **55 days paid tier / 1 day free tier**; `store=false` opts out but breaks `previous_interaction_id`/`background=true` | Stateless per call |

Sources: [Interactions API overview](https://ai.google.dev/gemini-api/docs/interactions-overview), [Why use it](https://ai.google.dev/gemini-api/docs/interactions), [Migration guide](https://ai.google.dev/gemini-api/docs/migrate-to-interactions), [full REST reference](https://ai.google.dev/api/interactions-api) (this is the field-by-field source of truth — the prose guides sometimes lag it).

**Recommendation for this hackathon:** default to the **Interactions API** — it's what
Google is actively building agent features on and the code is shorter. Drop to
`generateContent` only for the gaps above (explicit caching, custom safety thresholds,
local-process MCP servers) — the SDK client is the same object either way, so switching
per-call costs nothing.

```python
from google import genai
client = genai.Client()  # reads GEMINI_API_KEY

# Interactions API (new, GA, recommended)
interaction = client.interactions.create(model="gemini-3.7-flash", input="hello")
print(interaction.output_text)

# generateContent API (legacy, still fully supported)
response = client.models.generate_content(model="gemini-3.7-flash", contents="hello")
print(response.text)
```

**A parameter change to watch for**: as of the **21 Jul 2026** release, the classic
sampling knobs `temperature`, `top_p`, and `top_k` are **deprecated** across the Gemini
API. If you're copy-pasting older tutorial code that sets them, expect it to be ignored
or warned on — steer output via `thinking_level` (see [§6.4](#64-voice-activity-detection-vad-turn-control-thinking)
and [§11](#11-quick-reference)) and prompting instead.
[Source](https://ai.google.dev/gemini-api/docs/changelog) (Jul 21 2026 entry).

### 1.1 Managed agents — call Google's own agents directly

The Interactions API is explicitly "one endpoint for models **and** agents": swap the
`model` string for one of these and you get a full autonomous agent with no
orchestration code of your own — this is a legitimate shortcut for a 5-hour build if
your task fits one of them.

```python
interaction = client.interactions.create(
    model="antigravity-preview-05-2026",
    input="Investigate this repo, find the failing test, and propose a fix.",
)
```

| Model ID | What it does |
|---|---|
| `deep-research-preview-04-2026` | Plans and executes multi-step research across hundreds of sources, returns a cited report |
| `deep-research-max-preview-04-2026` | Same, tuned for maximum comprehensiveness |
| `antigravity-preview-05-2026` | General-purpose agent: plans, reasons, runs code, manages files, browses the web inside a sandboxed Linux VM |

All three are `-preview` — same "don't put it on the critical demo path untested" caveat
as [computer use](#7-computer-use) applies; test the exact prompt you'll use well before
you're on stage. [Source](https://ai.google.dev/api/interactions-api) (tool/agent model
list), [models overview](https://ai.google.dev/gemini-api/docs/models).

---

## 2. Function calling / tool use

### 2.1 Declare a tool and let the model call it (Interactions API)

```python
from google import genai
import json

set_light_values_declaration = {
    "name": "set_light_values",
    "description": "Sets the brightness and color temperature of a room light.",
    "parameters": {
        "type": "object",
        "properties": {
            "brightness": {"type": "integer", "description": "0-100"},
            "color_temp": {"type": "string", "enum": ["daylight", "cool", "warm"]},
        },
        "required": ["brightness", "color_temp"],
    },
}

def set_light_values(brightness, color_temp):
    return {"brightness": brightness, "color_temp": color_temp}

client = genai.Client()
interaction = client.interactions.create(
    model="gemini-3.7-flash",
    input="Turn the lights down to a romantic level",
    tools=[set_light_values_declaration],
)

fc_step = next(s for s in interaction.steps if s.type == "function_call")
if fc_step.name == "set_light_values":
    result = set_light_values(**fc_step.arguments)

# send the result back, chained via previous_interaction_id
final_interaction = client.interactions.create(
    model="gemini-3.7-flash",
    input=[{
        "type": "function_result",
        "name": fc_step.name,
        "call_id": fc_step.id,
        "result": [{"type": "text", "text": json.dumps(result)}],
    }],
    tools=[set_light_values_declaration],
    previous_interaction_id=interaction.id,
)
print(final_interaction.output_text)
```
[Source](https://ai.google.dev/gemini-api/docs/function-calling).

### 2.2 Automatic function calling (Python only, `generateContent`)

Pass a plain typed+docstringed Python function — the SDK builds the schema, executes
the call, and returns the final text for you (no manual round-trip):

```python
from google import genai
from google.genai import types

def get_current_temperature(location: str) -> dict:
    """Gets the current temperature for a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA
    """
    return {"temperature": 25, "unit": "Celsius"}

client = genai.Client()
config = types.GenerateContentConfig(tools=[get_current_temperature])
response = client.models.generate_content(
    model="gemini-3.7-flash", contents="What's the temperature in Boston?", config=config,
)
print(response.text)  # SDK already executed the function and folded in the result

# disable it if you want manual control:
config = types.GenerateContentConfig(
    tools=[get_current_temperature],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)
```
[Source](https://ai.google.dev/gemini-api/docs/generate-content/function-calling).

### 2.3 Parallel & compositional calls

The model can return **multiple** `function_call` steps in one response (parallel), or
call a second function using the first's result (compositional) — same code path as
above: iterate `interaction.steps` (or `response.function_calls` on `generateContent`)
and answer each one, in the order requested, before sending results back. Example (JS,
`generateContent`, parallel):

```javascript
const houseFns = [powerDiscoBall, startMusic, dimLights];
const config = {
  tools: [{ functionDeclarations: houseFns }],
  toolConfig: { functionCallingConfig: { mode: 'any' } },  // force a call — see 2.4
};
const chat = ai.chats.create({ model: 'gemini-3.7-flash', config });
const response = await chat.sendMessage({ message: 'Turn this place into a party!' });
for (const fn of response.functionCalls) { /* one entry per parallel call */ }
```
[Source](https://ai.google.dev/gemini-api/docs/generate-content/function-calling).

### 2.4 Forcing tool mode

**Interactions API** (current): pass `generation_config.tool_choice`, which takes a mode
of `auto` (default, model decides) / `any` (must call something) / `none` (temporarily
disable tools without removing declarations) / `validated` (per the REST schema; exact
semantics not documented in prose — treat as UNVERIFIED and test it). Constrain to
specific tools with `allowed_tools`:

```python
generation_config = {
    "tool_choice": {"allowed_tools": {"mode": "any", "tools": ["get_current_temperature"]}}
}
interaction = client.interactions.create(
    model="gemini-3.7-flash", input="...", tools=[...],
    generation_config=generation_config,
)
```
[Source: function-calling guide](https://ai.google.dev/gemini-api/docs/function-calling#function_calling_modes). The [REST field reference](https://ai.google.dev/api/interactions-api) documents `ToolChoiceConfig` as a flatter `{mode, tools}` shape (no `allowed_tools` wrapper) — the two may be equivalent nesting shown at different doc layers, or the guide may be ahead/behind the reference; smoke-test whichever shape your installed SDK version accepts before relying on it in a demo.

**`generateContent`** (legacy, same idea): `tool_config.function_calling_config.mode` ∈
`AUTO` / `ANY` (optionally + `allowed_function_names`) / `NONE`.

---

## 3. Built-in server-side tools

All are passed as tool objects (Interactions API: `{"type": "..."}`; generateContent:
tool-specific key) alongside or instead of your own function declarations, and are
billed per the [pricing page](https://ai.google.dev/gemini-api/docs/pricing#pricing_for_tools).

| Tool | `type` string | What it does |
|---|---|---|
| Google Search grounding | `google_search` | Grounds answers in live web results, returns `grounding_metadata` with citations |
| Google Maps grounding | `google_maps` (per [maps-grounding doc](https://ai.google.dev/gemini-api/docs/maps-grounding)) | Grounds answers in 250M+ Maps places/businesses; combine with `google_search` on Gemini 3.5 Flash+ |
| Code execution | `code_execution` | Model writes + runs Python in a sandbox, returns code + output |
| URL context | `url_context` | Model fetches and reads specific URLs you point it at |
| Computer use | `computer_use` | See [§7](#7-computer-use) |
| File Search (RAG) | `file_search` | Index your own docs, retrieval-augmented answers |

[Source: built-in tools table](https://ai.google.dev/gemini-api/docs/tools).

```python
interaction = client.interactions.create(
    model="gemini-3.1-pro-preview",
    input="Search for all details for the latest Euro.",
    tools=[{"type": "google_search"}, {"type": "url_context"}],
)
```
[Source](https://ai.google.dev/gemini-api/docs/gemini-3).

```python
interaction = client.interactions.create(
    model="gemini-3.5-flash",
    input="Calculate the 50th Fibonacci number.",
    tools=[{"type": "code_execution"}],
)
print(interaction.outputs[-1].text)
```
[Source](https://github.com/googleapis/python-genai).

**Combining built-in + custom tools in one call** — the model picks whichever is
relevant per turn:

```python
interaction = client.interactions.create(
    model="gemini-3-flash-preview",
    input="What is the northernmost city in the United States? What's the weather like there today?",
    tools=[{"type": "google_search"}, getWeather],  # getWeather is your own function declaration
)
```
[Source](https://ai.google.dev/gemini-api/docs/gemini-3).

**Gemini 3 also lets you combine built-in tools with structured output** — see
`response_format` in [§4](#4-structured-output--json-schema) — supported for Search,
URL Context, Code Execution, File Search, and Function Calling
([source](https://ai.google.dev/gemini-api/docs/structured-output)).

---

## 4. Structured output / JSON schema

Pass a JSON Schema (or a Pydantic model / Zod schema converted to one) via
`response_format` (Interactions API) or `response_mime_type` + `response_schema`
(generateContent). Supports recursive schemas via `"$ref": "#"`.

```python
from google import genai
from pydantic import BaseModel, Field
from typing import List

class Employee(BaseModel):
    name: str
    employee_id: int
    reports: List["Employee"] = Field(default_factory=list)

client = genai.Client()
interaction = client.interactions.create(
    model="gemini-3.7-flash",
    input="Generate an org chart. Alice manages Bob and Charlie. Bob manages David.",
    response_format={
        "type": "text",
        "mime_type": "application/json",
        "schema": Employee.model_json_schema(),
    },
)
employee = Employee.model_validate_json(interaction.output_text)
```
[Source](https://ai.google.dev/gemini-api/docs/structured-output).

JS/Zod equivalent:

```javascript
import * as z from "zod";
const employeeJsonSchema = { /* ...same JSON schema... */ };
const employeeSchema = z.fromJSONSchema(employeeJsonSchema);
const interaction = await client.interactions.create({
  model: "gemini-3.7-flash", input: prompt,
  response_format: { type: 'text', mime_type: 'application/json', schema: employeeJsonSchema },
});
const employee = employeeSchema.parse(JSON.parse(interaction.output_text));
```
[Source](https://ai.google.dev/gemini-api/docs/structured-output).

For enum-constrained fields, use standard JSON Schema `"enum": [...]` on any string
property — same mechanism as `color_temp` in the function-calling example above.
`generateContent` uses the equivalent `response_mime_type="application/json"` +
`response_schema=<pydantic model or list[Model]>` config keys
([source](https://ai.google.dev/gemini-api/docs/batch-mode) — see the batch example, which
uses this exact legacy form).

---

## 5. MCP (Model Context Protocol) support

There are **two** ways to attach an MCP server, and which one you want depends on where
the server lives. Corrects an earlier draft of this doc (and several August-2026 blog
posts) that said Gemini didn't support remote MCP yet — it does, as a native Interactions
API tool.

### 5.1 Remote MCP (Interactions API) — the fast path for a hackathon

If your MCP server is reachable over HTTP (deployed, tunneled via ngrok, etc.), just
declare it as a tool — **no client library, no local process**:

```python
interaction = client.interactions.create(
    model="gemini-3.7-flash",
    input="What is the weather in London today?",
    tools=[{
        "type": "mcp_server",
        "name": "weather_mcp",           # snake_case only — no hyphens allowed
        "url": "https://your-server.example.com/mcp",
        "headers": {"Authorization": "Bearer <token>"},   # optional, for auth
        "allowed_tools": ["get_weather"],                 # optional allow-list
    }],
)
```
Constraints: **Streamable HTTP servers only — SSE servers are not supported**, and the
`name` must be `snake_case` (no `-`). [Source: function-calling guide, "Remote MCP"
section](https://ai.google.dev/gemini-api/docs/function-calling), field reference at
[ai.google.dev/api/interactions-api](https://ai.google.dev/api/interactions-api).

### 5.2 Local MCP server (`generateContent`, experimental)

If your MCP server only runs as a local process (stdio) and you have nothing to deploy
in the next 5 hours, attach it via the SDK's experimental MCP support instead — hand the
SDK an `mcp` `ClientSession` directly and it lists + calls the server's tools for you:

```bash
pip install mcp
```

```python
import asyncio
from datetime import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai

client = genai.Client()
server_params = StdioServerParameters(
    command="npx", args=["-y", "@philschmid/weather-mcp"], env=None,
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await client.aio.models.generate_content(
                model="gemini-3.7-flash",
                contents=f"What is the weather in London in {datetime.now():%Y-%m-%d}?",
                config=genai.types.GenerateContentConfig(
                    tools=[session],  # <-- the whole MCP session becomes a tool
                ),
            )
            print(response.text)

asyncio.run(run())
```
Sources: [python-genai README](https://github.com/googleapis/python-genai) (canonical), cross-confirmed on [ai.google.dev function-calling (legacy)](https://ai.google.dev/gemini-api/docs/generate-content/function-calling). Marked experimental by Google; passing `tools=[session]` gets automatic tool calling for free, disable with `automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)`. Not confirmed as available on the Interactions API — use §5.1 there instead.

**Bottom line for this hackathon**: if the MCP server you want to use (yours or a
third-party one) can be reached by URL, use §5.1 — it's less code and it's on the
current, recommended API surface.

---

## 6. Live API (realtime voice/video agents)

This is the highest-leverage demo capability on this list — one websocket session gives
you a full-duplex voice agent with interruption handling built in.

### 6.1 Model & minimal session

Current model: **`gemini-3.1-flash-live-preview`** (low-latency audio-to-audio,
replaces the now-shut-down `gemini-2.5-flash-preview-native-audio-dialog` and
`gemini-live-2.5-flash-preview`, both retired Dec 9 2025 —
[changelog](https://ai.google.dev/gemini-api/docs/changelog)). A native-audio variant
with emotion-aware "Affective Dialog" and "Proactive Audio" turn-taking also exists as
`gemini-2.5-flash-native-audio-latest` (UNVERIFIED exact current name — confirm on the
[models page](https://ai.google.dev/gemini-api/docs/models) before demo day, these get
renamed often).

```python
import asyncio
from google import genai
from google.genai import types

client = genai.Client()
model = "gemini-3.1-flash-live-preview"
config = {"response_modalities": ["AUDIO"], "output_audio_transcription": {}}

async def main():
    async with client.aio.live.connect(model=model, config=config) as session:
        await session.send_client_content(
            turns={"role": "user", "parts": [{"text": "Hello? Gemini are you there?"}]},
            turn_complete=True,
        )
        async for response in session.receive():
            if response.server_content.model_turn:
                print("Model turn:", response.server_content.model_turn)
            if response.server_content.output_transcription:
                print("Transcript:", response.server_content.output_transcription.text)

asyncio.run(main())
```
[Source](https://ai.google.dev/gemini-api/docs/live-api/capabilities).

Streaming your own mic audio in (16kHz PCM):

```python
await session.send_realtime_input(
    audio=types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
)
```
[Source](https://ai.google.dev/gemini-api/docs/live-api/capabilities).

### 6.2 Voices

Set voice via `speechConfig`. Native-audio output supports **30 HD voices across 24
languages** (listen to them in AI Studio); note `generateContent`-based TTS has a
slightly different voice set than Live — check the
[speech generation doc](https://ai.google.dev/gemini-api/docs/speech-generation#voices)
for the full name list rather than guessing a voice name.

```javascript
const config = {
  responseModalities: [Modality.AUDIO],
  speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: "Kore" } } },
};
```
[Source](https://ai.google.dev/gemini-api/docs/live-api/capabilities).

### 6.3 Tool use inside Live sessions

Live sessions support Google Search grounding and your own function declarations
concurrently with audio, plus **async / non-blocking function responses** so a slow
tool call doesn't freeze the conversation:

```javascript
const tools = [{ googleSearch: {} }];
const config = { responseModalities: [Modality.AUDIO], tools };
```
```python
function_response = types.FunctionResponse(
    id=fc.id, name=fc.name,
    response={"result": "ok", "scheduling": "INTERRUPT"},  # or WHEN_IDLE / SILENT
)
```
`scheduling` controls whether the tool result interrupts the model immediately,
waits for a natural pause, or is applied silently. [Source](https://ai.google.dev/gemini-api/docs/live-tools).

### 6.4 Voice Activity Detection (VAD), turn control, thinking

```python
config = {
    "response_modalities": ["AUDIO"],
    "realtime_input_config": {
        "automatic_activity_detection": {
            "disabled": False,
            "start_of_speech_sensitivity": types.StartSensitivity.START_SENSITIVITY_LOW,
            "end_of_speech_sensitivity": types.EndSensitivity.END_SENSITIVITY_LOW,
            "prefix_padding_ms": 20,
            "silence_duration_ms": 100,
        }
    },
}
```
Disable auto-VAD and drive turns manually with `activityStart`/`activityEnd` if you
need push-to-talk. Live also supports a `thinking_config` (`thinking_level`,
`include_thoughts=True`) for reasoning-visible responses, and
`enable_affective_dialog=True` for emotion-aware native audio.
[Source](https://ai.google.dev/gemini-api/docs/live-api/capabilities).

`thinking_level` (used here and in §2/§11) is documented in the REST schema with four
possible values — `minimal`, `low`, `medium`, `high` — but **not every model accepts
all four**: `gemini-3.7-flash`'s own guide documents only `low`/`medium`/`high` (default
`medium`), while some Gemini 3.1 models default to `minimal`. Check the specific model's
page rather than assuming — an unsupported value is a plausible source of a silent demo
failure. [Source](https://ai.google.dev/api/interactions-api), [Gemini thinking guide](https://ai.google.dev/gemini-api/docs/thinking).

### 6.5 Session resumption & long sessions (defends against the #1 Live demo failure: silent disconnects)

The server periodically resets the WebSocket and sends a `GoAway` message with
`time_left` before it does — handle it and reconnect using a resumption handle so a
30-minute demo doesn't die mid-sentence:

```python
async with client.aio.live.connect(
    model=model,
    config=types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        session_resumption=types.SessionResumptionConfig(handle=previous_session_handle),
    ),
) as session:
    async for message in session.receive():
        if message.session_resumption_update and message.session_resumption_update.resumable:
            previous_session_handle = message.session_resumption_update.new_handle
```
Resumption tokens are valid for **2 hours** after termination. For long context, also
enable `context_window_compression=types.ContextWindowCompressionConfig(sliding_window=types.SlidingWindow())`.
[Source](https://ai.google.dev/gemini-api/docs/live-session).

---

## 7. Computer use

> ⚠️ **This tool is Preview status, not GA.** Every model that runs it
> (`gemini-2.5-computer-use-preview-10-2025`, and the built-in support in
> `gemini-3-pro-preview`/`gemini-3-flash-preview`) has "preview" in the name for a
> reason. **Do not put it on the critical path of a live stage demo** — preview
> endpoints are the ones most likely to change behavior, rate-limit harder, or throw an
> unfamiliar error at exactly the wrong moment. Record a working run as your fallback
> video, and have a non-computer-use path to the same "wow moment" if this is your
> centerpiece feature.

**Status: public preview since June 24 2026.** The model looks at a screenshot and
returns a `function_call` describing a UI action (click at (x,y), type text, scroll,
etc.); you execute it (e.g. via Playwright) and feed the result back.

```python
from google import genai
client = genai.Client()
interaction = client.interactions.create(
    model='gemini-2.5-computer-use-preview-10-2025',
    input="Search for highly rated smart fridges on Google Shopping.",
    tools=[{
        "type": "computer_use",
        "environment": "browser",  # confirmed value; no other environment enum values confirmed in docs
        "excluded_predefined_functions": ["drag_and_drop"],  # optional
    }],
)
```
[Source](https://ai.google.dev/gemini-api/docs/computer-use).

Executing an action (coordinates are normalized 0–1000, scale to real pixels):

```python
def denormalize_x(x, screen_width): return int(x / 1000 * screen_width)
def denormalize_y(y, screen_height): return int(y / 1000 * screen_height)

for function_call in [s for s in interaction.steps if s.type == "function_call"]:
    fname, args = function_call.name, function_call.arguments
    if fname in ("click", "click_at"):
        page.mouse.click(denormalize_x(args["x"], w), denormalize_y(args["y"], h))
    # ...double_click, right_click, move, long_press, type, scroll, key_combination, etc.
```
[Source](https://ai.google.dev/gemini-api/docs/computer-use).

**Safety confirmation** — some actions (e.g. anything that looks destructive/irreversible)
come back with a `safety_decision` payload the model wants a human to confirm before it
proceeds:

```python
if 'safety_decision' in function_call.arguments:
    decision = get_safety_confirmation(function_call.arguments['safety_decision'])
    if decision == "TERMINATE":
        break
    action_result["safety_acknowledgement"] = True
```
[Source](https://ai.google.dev/gemini-api/docs/computer-use).

**Model options**: dedicated `gemini-2.5-computer-use-preview-10-2025` (browser-optimized,
used in all current doc examples), and — per Google's own Jan 29 2026 changelog entry —
computer-use capability is also built directly into `gemini-3-pro-preview` and
`gemini-3-flash-preview`, no separate model needed. As of Aug 13 2026 there's also a
`gemini-3.1-pro-preview-customtools` endpoint tuned for mixing bash tools with your
own custom tools. Treat the exact model choice as something to re-check against
[the computer-use doc](https://ai.google.dev/gemini-api/docs/computer-use) on the day,
since this is a fast-moving preview feature.

---

## 8. Long-running / async

### 8.1 Batch API — 50% cheaper, use for anything not in the live demo path

Only available via `generateContent` (not Interactions API yet). Two input shapes:
inline requests, or a JSONL file via the File API.

```python
from google import genai
client = genai.Client()

inline_requests = [{
    'contents': [{'parts': [{'text': 'List a few popular cookie recipes.'}], 'role': 'user'}],
    'config': {'response_mime_type': 'application/json', 'response_schema': list[Recipe]},
}]
job = client.batches.create(model="gemini-3.7-flash", src=inline_requests,
                             config={'display_name': "structured-output-job-1"})

while True:
    job = client.batches.get(name=job.name)
    if job.state.name in ('JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED', 'JOB_STATE_CANCELLED', 'JOB_STATE_EXPIRED'):
        break
```
Target turnaround is 24h but usually much faster; concurrent batch limit 100, input
file size limit 2GB, storage limit 20GB. Optional webhook instead of polling:
`client.webhooks.create(name=..., subscribed_events=["batch.succeeded", "batch.failed"], uri=...)`.
[Source](https://ai.google.dev/gemini-api/docs/batch-mode), [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits#batch-api-rate-limits).

### 8.2 Context caching — cut cost fast on repeated large context

**Important split**: the Interactions API only supports **implicit** caching (automatic,
no code needed — repeated prefixes across turns get cheaper on their own). **Explicit**
caching (you create/name/TTL a cache object yourself, for a big system prompt or
document you reuse across many independent requests) is `generateContent`-only:

```python
# generateContent only
for cache in client.caches.list(): print(cache)
cache = client.caches.get(name=name)
client.caches.update(name=cache.name, config={"ttl": "7200s"})  # 2 hours
```
[Source](https://ai.google.dev/gemini-api/docs/caching), [explicit caching doc](https://ai.google.dev/gemini-api/docs/generate-content/caching).

For a 5-hour hackathon: don't build explicit caching unless you're re-sending a large
fixed document/context across many calls — implicit caching on the Interactions API
already gets you most of the win for free, especially if you keep chaining
`previous_interaction_id`.

### 8.3 File API — upload once, reference everywhere (images/video/audio/PDF/JSONL)

```python
uploaded_file = client.files.upload(
    file='my-batch-requests.jsonl',
    config=types.UploadFileConfig(display_name='my-batch-requests', mime_type='jsonl'),
)
```
[Source](https://ai.google.dev/gemini-api/docs/batch-mode) (same call is used for any
large upload, not just batch input — see [Files API doc](https://ai.google.dev/gemini-api/docs/files) for the full supported-type list and the 48-hour retention window before you build around it).

### 8.4 Background execution (Interactions API)

```python
interaction = client.interactions.create(model="gemini-3.7-flash", input="...", background=True)
# poll:
result = client.interactions.get(interaction.id)
```
Use for any single call you expect to run long (e.g. a big code-execution or deep-research
step) without holding an HTTP connection open. [Source](https://ai.google.dev/gemini-api/docs/quickstart) (step 11); see [Background execution guide](https://ai.google.dev/gemini-api/docs/background-execution) for the full contract.

---

## 9. Multi-turn state, chat sessions, and cheap agent memory

**Three ways to hold conversation state, cheapest/easiest first:**

1. **Interactions API chaining** — just pass `previous_interaction_id`; the server
   keeps history (and gets better cache hit rates on it) by default (`store=true`):
   ```python
   i1 = client.interactions.create(model="gemini-3.7-flash", input="I have 2 dogs in my house.")
   i2 = client.interactions.create(model="gemini-3.7-flash", input="How many paws are in my house?",
                                    previous_interaction_id=i1.id)
   ```
   Opt into stateless mode with `store=False` if you don't want Google retaining the
   turn server-side, and manage your own `history` list of `step.model_dump()` entries
   instead (see the [migrate-to-interactions doc](https://ai.google.dev/gemini-api/docs/migrate-to-interactions) for the full manual-history pattern).
   [Source](https://ai.google.dev/gemini-api/docs/text-generation).

2. **`chats.create()` helper** (works on both APIs) — simplest for a straightforward
   back-and-forth, SDK manages history in memory for you:
   ```python
   chat = client.chats.create(model="gemini-3.7-flash")
   chat.send_message("Hi, my name is Phil.")
   chat.send_message("What is my name?")
   ```
   [Source](https://ai.google.dev/gemini-api/docs/migrate-to-interactions).

3. **Manual `contents` history** (`generateContent`) — full control, needed if you're
   persisting conversations yourself (e.g. in your own DB) across process restarts:
   ```python
   response = client.models.generate_content(model="gemini-3.7-flash", contents=[
       types.Content(role="user", parts=[types.Part.from_text(text="Hi, I'm Phil.")]),
       types.Content(role="model", parts=[types.Part.from_text(text="Hi Phil!")]),
       types.Content(role="user", parts=[types.Part.from_text(text="What is my name?")]),
   ])
   ```

**Cheap persistent agent memory pattern for a hackathon**: store the `history`/
`interaction.steps` list as JSON per user/session in whatever DB you already have
(SQLite/Redis/a JSON file is fine for a demo); reload it and pass it back as `input`/
`contents` on the next call. Don't build a vector store for memory in a 5-hour build —
implicit caching + a raw history list is enough unless your rubric specifically rewards
RAG.

---

## 10. Safety settings & the failure modes that break demos

### 10.1 Safety settings (`generateContent`; not yet configurable on Interactions API)

```python
from google.genai import types
response = client.models.generate_content(
    model="gemini-3.7-flash", contents="Some potentially unsafe prompt",
    config=types.GenerateContentConfig(safety_settings=[
        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                             threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
    ]),
)
```
Threshold values (API string → behavior): `OFF` (filter off) · `BLOCK_NONE` (always
show) · `BLOCK_ONLY_HIGH` · `BLOCK_MEDIUM_AND_ABOVE` · `BLOCK_LOW_AND_ABOVE` (most
aggressive) · `HARM_BLOCK_THRESHOLD_UNSPECIFIED` (default). Harm categories include at
least `HARM_CATEGORY_HARASSMENT`, `HARM_CATEGORY_HATE_SPEECH`,
`HARM_CATEGORY_SEXUALLY_EXPLICIT`, `HARM_CATEGORY_DANGEROUS_CONTENT`, and
`HARM_CATEGORY_CIVIC_INTEGRITY`. There's also an optional `method` field
(`severity` vs `probability` scoring). Additional filters are **off by default** —
you're opting into stricter blocking, not relaxing it, in most demo scenarios.
[Source](https://ai.google.dev/gemini-api/docs/safety-settings).

### 10.2 Failure modes that will bite you on stage, and the defense for each

| Failure | What it looks like | Defense |
|---|---|---|
| **Blocked response** | `finish_reason == "SAFETY"`, empty `.text` | Check `response.candidates[0].finish_reason` and `prompt_feedback` before reading `.text`/`.output_text`; never assume it's populated. Loosen `safety_settings` only for categories you understand, and only on `generateContent`. |
| **Empty candidates** | `response.candidates` is `[]` or `.text` raises | Same check as above — wrap output access, fall back to a canned "let me rephrase that" line in the demo rather than crashing. |
| **429 quota/rate-limit** | `RESOURCE_EXHAUSTED` | Exponential backoff with jitter (`2^attempt + random(0,1)` seconds), cap at 5–8 retries. Free tier is tight (e.g. `gemini-3-flash-preview`: ~10 RPM / 250K TPM / 1,500 RPD) — **get a paid-tier key before demo day**, don't discover this live. Spend-based limits also apply per usage tier (Tier 1: $10/10-min window) and also return 429. [Source](https://ai.google.dev/gemini-api/docs/rate-limits). |
| **API errors generally** | Any non-2xx | Catch `google.genai.errors.APIError`, which exposes `.code` and `.message` — log both before retrying blind. [Source](https://github.com/googleapis/python-genai). |
| **Preview/experimental model instability** | Higher error rates, tighter limits, occasional removal (see the Live API model shutdowns in the changelog) | Pin the exact model string you tested with, keep a fallback model string ready to swap in a config var, and re-check [the models page](https://ai.google.dev/gemini-api/docs/models) the morning of the demo. [Source](https://ai.google.dev/gemini-api/docs/changelog). |

---

## 11. Quick reference

**Model IDs seen live in current docs (Aug 2026)** — these churn fast; treat any name
here as "confirmed as of this doc fetch," not a permanent contract. Re-check
[ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models) or
call `client.models.get(model=...)` before you hard-code one into a demo you'll run in 4
hours.

| Model ID | Status | Use for | Notes |
|---|---|---|---|
| `gemini-3.7-flash` | **GA** (13 Aug 2026) | General agent default | Most current, most stable choice — see [source](https://ai.google.dev/gemini-api/docs/changelog) |
| `gemini-3.6-flash` | GA (21 Jul 2026) | Fallback if 3.7 misbehaves | Better token efficiency than 3.5 Flash |
| `gemini-3.5-flash-lite` | GA (21 Jul 2026) | High-volume, cost-sensitive subagent calls | Low latency |
| `gemini-3-flash-preview` | Preview | Older default, still has computer-use built in | Superseded by 3.7 Flash for general use |
| `gemini-3.1-pro-preview` | Preview | Hard reasoning, complex multimodal | 1M in / 64K out context |
| `gemini-3.1-flash-live-preview` | Preview | Live API voice/video | Current flagship Live model |
| `gemini-2.5-computer-use-preview-10-2025` | Preview | Dedicated computer-use / browser agents | See [§7](#7-computer-use) warning |
| `gemini-3-pro-image-preview` ("Nano Banana Pro") | Preview | Highest-quality image gen | |
| `gemini-3.1-flash-image-preview` ("Nano Banana 2") | Preview | High-volume, cheaper image gen | |
| `deep-research-preview-04-2026` / `antigravity-preview-05-2026` | Preview | Managed agents, see [§1.1](#11-managed-agents--call-googles-own-agents-directly) | Called via `model=` on the same `interactions.create()` |

Pricing snapshot (per 1M tokens, input/output; check [pricing page](https://ai.google.dev/gemini-api/docs/pricing) for current numbers before budgeting API spend):
`gemini-3.7-flash`: **$0.75/$3.75 introductory** (through 31 Dec 2026, then $1.50/$7.50)
· `gemini-3.1-flash-lite`: $0.25/$1.50 · `gemini-3-flash-preview`: $0.50/$3 ·
`gemini-3.1-pro-preview`: $2/$12 (<200K context) or $4/$18 (>200K context).
[Sources](https://ai.google.dev/gemini-api/docs/gemini-3), [what's new in 3.7 Flash](https://ai.google.dev/gemini-api/docs/latest-model), [pricing page](https://ai.google.dev/gemini-api/docs/pricing).

`thinking_level`: `low` / `medium` (default on 3.5+/3.6/3.7 Flash) / `high` — see the
caveat on `minimal` in [§6.4](#64-voice-activity-detection-vad-turn-control-thinking).
**`temperature`/`top_p`/`top_k` are deprecated** as of 21 Jul 2026 — don't rely on them.

**Retry pattern** (copy-paste):

```python
import time, random
from google.genai import errors

def call_with_backoff(fn, *args, max_retries=6, **kwargs):
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except errors.APIError as e:
            if e.code != 429 or attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt + random.random())
```

---

### Sources index

- [Interactions API overview](https://ai.google.dev/gemini-api/docs/interactions-overview) · [Why use it / features](https://ai.google.dev/gemini-api/docs/interactions) · [Migration guide](https://ai.google.dev/gemini-api/docs/migrate-to-interactions) · [Full REST reference](https://ai.google.dev/api/interactions-api)
- [Gemini 3 developer guide](https://ai.google.dev/gemini-api/docs/gemini-3) · [What's new in Gemini 3.7 Flash](https://ai.google.dev/gemini-api/docs/latest-model) · [Gemini thinking](https://ai.google.dev/gemini-api/docs/thinking)
- [Function calling (Interactions)](https://ai.google.dev/gemini-api/docs/function-calling) · [Function calling (legacy generateContent)](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)
- [Tools overview](https://ai.google.dev/gemini-api/docs/tools) · [Google Search grounding](https://ai.google.dev/gemini-api/docs/grounding) · [Maps grounding](https://ai.google.dev/gemini-api/docs/maps-grounding) · [URL context](https://ai.google.dev/gemini-api/docs/url-context) · [Code execution](https://ai.google.dev/gemini-api/docs/code-execution)
- [Structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [python-genai SDK (MCP support)](https://github.com/googleapis/python-genai)
- [Live API overview](https://ai.google.dev/gemini-api/docs/live) · [Live API capabilities](https://ai.google.dev/gemini-api/docs/live-api/capabilities) · [Live API get started](https://ai.google.dev/gemini-api/docs/live-api/get-started-sdk) · [Live tool use](https://ai.google.dev/gemini-api/docs/live-tools) · [Live session management](https://ai.google.dev/gemini-api/docs/live-session)
- [Computer use](https://ai.google.dev/gemini-api/docs/computer-use)
- [Batch API](https://ai.google.dev/gemini-api/docs/batch-mode) · [Context caching](https://ai.google.dev/gemini-api/docs/caching) · [Explicit caching (legacy)](https://ai.google.dev/gemini-api/docs/generate-content/caching) · [Files API](https://ai.google.dev/gemini-api/docs/files)
- [Text generation / multi-turn](https://ai.google.dev/gemini-api/docs/text-generation)
- [Safety settings](https://ai.google.dev/gemini-api/docs/safety-settings)
- [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) · [Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Changelog / release notes](https://ai.google.dev/gemini-api/docs/changelog)
- [Managed Agents (remote MCP, background tasks) blog](https://blog.google/innovation-and-ai/technology/developers-tools/expanding-managed-agents-gemini-api/)
