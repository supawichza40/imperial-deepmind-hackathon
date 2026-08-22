# Google agent frameworks & tooling — hackathon fit map

Researched 2026-08-22 for "UK AI Agent Lab: Gemini Edition" (hacking 12:30–17:30 today). Everything below was verified live against official sources today; anything I couldn't verify is marked UNVERIFIED.

## Decision table

| Stack | Time-to-first-demo | Risk in a 5h window | Why judges (DeepMind mentors) care |
|---|---|---|---|
| **ADK (Python)** | 15–30 min to a running single agent, 2–3h to a multi-agent demo | Low | It's Google's own agent framework, actively developed (weekly point releases), mentors will know it cold |
| **ADK MCP tools (`McpToolset`)** | ~0 extra — one import | Low | Shows you can plug in existing tool ecosystems fast, not just prompt an LLM |
| **A2A protocol** | +1–2h for a second real agent + handshake | Medium — payoff only shows if you build it *and* narrate it well | Google-originated, now Linux Foundation-governed with AWS/Microsoft/Salesforce/SAP/ServiceNow on the steering committee — a real interoperability story, not vendor lock-in |
| **Gemini CLI (as your own coding assistant)** | N/A for free/individual use today | High if you assume the old free tier — it was switched off | Not a demo component; only matters if your team plans to code the hack *with* it |
| **Antigravity / Antigravity CLI** | Fast — this is what replaced free-tier Gemini CLI | Low–Medium (product is ~3 months old) | It's literally what Google now points free users to; using it shows you're current |
| **Google AI Studio "Build" (vibe coding)** | 5–15 min prompt → full-stack app with Firebase | Low for a throwaway UI shell, Medium if you rely on it for the *whole* app | Extremely fast visual payoff for judges; weak "we built the agent" story on its own |
| **Vertex AI Agent Builder / Agent Runtime (formerly Agent Engine)** | +1–2h minimum for GCP project/billing/IAM setup | **High — a trap in 5 hours** | Production-grade, but the setup tax eats your build window; only worth it if a mentor specifically asks "is this deployed" |
| **Jules** | N/A live — it's an async background agent | Trap for a live build | Built for hand-off tasks (bug fixes, version bumps) you check back on later, not real-time pair coding under a clock |
| **Firebase Studio** | N/A — being sunset | Avoid | Google is winding it down (accessible only until 2027-03-22); don't build new work on it today |

**Bottom line:** build on **ADK (Python) + `adk web`**, reach for **MCP** the moment you need an external tool, treat **A2A** as a stretch differentiator only if the core demo is solid early, and stay away from **Agent Runtime/Vertex Agent Builder**, **Jules**, and **Firebase Studio** for today's build. See the [full recommendation](#8-recommendation) at the end.

---

## 1. Agent Development Kit (ADK)

**What it is:** Google's open-source, code-first agent framework. Optimized for Gemini but model-agnostic. Current PyPI release is **`google-adk` 2.7.1** (released 2026-08-17, part of the "ADK 2.0" line), and it ships in **Python, TypeScript, Go, Java, and Kotlin** — Go just went GA at 2.0 with graph workflows and collaborative agents. [google.github.io/adk-docs](https://google.github.io/adk-docs/), [pypi.org/project/google-adk](https://pypi.org/project/google-adk/)

### Install

```bash
# Python
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate.bat
pip install google-adk
pip show google-adk            # verify

# TypeScript (also grabs the dev UI package)
npm install @google/adk @google/adk-devtools

# Go (requires Go 1.25+, ADK Go v2.0.0)
go mod init example.com/my-agent
go get google.golang.org/adk/v2
```
[google.github.io/adk-docs/get-started/installation](https://google.github.io/adk-docs/get-started/installation/)

### Minimal runnable agent

```python
from google.adk import Agent
from google.adk.tools import google_search

agent = Agent(
    name="researcher",
    model="gemini-flash-latest",
    instruction="You help users research topics thoroughly.",
    tools=[google_search],
)
```
Run it interactively with the built-in dev UI:
```bash
adk web
```
[google.github.io/adk-docs](https://google.github.io/adk-docs/) (home page code sample), dev UI confirmed via [evaluate docs](https://google.github.io/adk-docs/evaluate/)

### Core primitives
- **Agent** — `LlmAgent` for reasoning, or deterministic **workflow agents** (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) that control execution without calling an LLM themselves.
- **Tool** — function calling, built-in tools (Google Search, code execution), or external tools via MCP (below).
- **Callbacks** — hook points in the agent lifecycle for logging/guardrails.
- **Session & State** — `SessionService` manages one conversation thread (`Session`, its `Events`, its `State`); in-memory implementations exist for fast local dev but lose everything on restart, plus cloud-backed options for persistence.
- **Memory** — `MemoryService`, a separate, searchable cross-session store (distinct from per-conversation `State`).
- **Artifact management** — save/load files or binary data tied to a session or user.
- **Code execution** and **Planning** as advanced capabilities.
[google.github.io/adk-docs/get-started/about](https://google.github.io/adk-docs/get-started/about/), [google.github.io/adk-docs/sessions](https://google.github.io/adk-docs/sessions/)

### Multi-agent patterns
ADK's "workflow agents" are the building blocks for orchestration without hand-rolling control flow:
- `SequentialAgent` — runs sub-agents in order, passing state forward.
- `ParallelAgent` — fans sub-agents out concurrently.
- `LoopAgent` — repeats a sub-agent (or pipeline) until a condition/iteration cap.
- A **coordinator/dispatcher** pattern is just an `LlmAgent` with other agents listed as `sub_agents`, letting the LLM route dynamically instead of a fixed pipeline.
[google.github.io/adk-docs/agents/workflow-agents](https://google.github.io/adk-docs/agents/workflow-agents/), [google.github.io/adk-docs/workflows](https://google.github.io/adk-docs/workflows/)

### Evaluation
Four ways to evaluate, from lightest to heaviest:
- **`adk web`** — interactive evaluation through the same dev UI, with a **Trace** tab (Event / Request / Response / Graph views per interaction) for debugging any session, not just eval runs.
- **`pytest`** — wire evaluation into your normal test suite.
- **`adk eval`** — CLI runner against an `EvalSet` file for quick regression checks.
- **`adk conformance`** — automated diffing against baseline files to catch regressions.
[google.github.io/adk-docs/evaluate](https://google.github.io/adk-docs/evaluate/)

### Deployment — three real paths
- **Cloud Run** (fastest for a public demo URL):
  ```bash
  gcloud auth login
  gcloud config set project <your-project-id>
  adk deploy cloud_run
  ```
  [google.github.io/adk-docs/deploy/cloud-run](https://google.github.io/adk-docs/deploy/cloud-run/)
- **Agent Runtime** (Vertex AI's managed agent hosting — this is the current name for what used to be called "Agent Engine", now part of the rebranded **Gemini Enterprise Agent Platform**). Two paths: a "standard" step-by-step deployment via Cloud Console + ADK CLI, or an accelerated "Agents CLI deployment" that sets up CI/CD and infra-as-code for you (needs a billing-enabled GCP project). Supported from ADK Python/Go v1.2.0+. [google.github.io/adk-docs/deploy/agent-runtime](https://google.github.io/adk-docs/deploy/agent-runtime/)
- **GKE** — for full control or running open-weight models yourself. [google.github.io/adk-docs/deploy](https://google.github.io/adk-docs/deploy/)

### Language SDKs
Python, TypeScript, Go, Java, Kotlin are all first-class today (shown side-by-side on the docs homepage with equivalent code samples in each). [google.github.io/adk-docs](https://google.github.io/adk-docs/)

---

## 2. A2A (Agent2Agent) protocol

**What it is:** An open protocol so independently-built agents can discover each other's capabilities and talk, regardless of framework or vendor. Originally built by Google, then **donated to the Linux Foundation**; it's now run by a Technical Steering Committee with **AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP, and ServiceNow**. [a2a-protocol.org/latest](https://a2a-protocol.org/latest/)

**Current spec version:** the latest *released* version is **1.0** — protocol version negotiation uses `Major.Minor` (e.g. `1.0`); patch numbers don't affect compatibility and shouldn't appear in Agent Cards. [a2a-protocol.org/latest/specification](https://a2a-protocol.org/latest/specification/)

### Agent Card
A publicly hosted JSON document describing an agent — its capabilities/skills, endpoint URL, auth methods, etc. Discovery is normally via a well-known path:
```
GET https://{agent-server-domain}/.well-known/agent-card.json
```
following RFC 8615. A client can also call the JSON-RPC method `GetExtendedAgentCard` for a fuller card after initial contact. Agent Cards **MAY** be digitally signed (JWS, RFC 7515) so a receiving agent can verify authenticity — this is the kind of trust primitive worth mentioning if a mentor asks about security. [a2a-protocol.org/latest/topics/agent-discovery](https://a2a-protocol.org/latest/topics/agent-discovery/), [a2a-protocol.org/latest/specification](https://a2a-protocol.org/latest/specification/)

### SDK
```bash
pip install a2a-sdk        # currently 1.1.2
```
[pypi.org/project/a2a-sdk](https://pypi.org/project/a2a-sdk/)

### A concrete on-ramp
Google's own codelab wires MCP + ADK + A2A together end to end (a "currency agent" example) — this is the fastest way to see the three pieces interact rather than reading spec text: [codelabs.developers.google.com/codelabs/currency-agent](https://codelabs.developers.google.com/codelabs/currency-agent)

### Is it a realistic hackathon differentiator today?
Yes, but only as a **second-stage** feature. Transport (JSON-RPC 2.0) and the Agent Card model are simple enough to stand up in an hour once you already have two working ADK agents — expose each as an A2A server, publish an Agent Card, have one agent's tool call be "ask the other agent over A2A." The differentiator for judges is the *story* ("two independently-deployable agents built with different owners/frameworks talking over an open, Linux-Foundation-governed protocol"), not raw code volume. Don't start with A2A; add it once your single-agent demo already works.

---

## 3. MCP in Google's stack

Google's stack consumes and exposes MCP in two directions inside ADK:

1. **ADK agent as an MCP client** — `McpToolset` is the primitive. Add an `McpToolset` instance to an agent's `tools` list and it manages the connection to an MCP server for you: `StdioConnectionParams` for a local server process, `SseConnectionParams` for a remote one over Server-Sent Events. The MCP server's tools then show up to your `LlmAgent` exactly like native ADK tools. [github.com/google/adk-docs — tools-custom/mcp-tools.md](https://github.com/google/adk-docs/blob/main/docs/tools-custom/mcp-tools.md)
2. **ADK tools exposed via an MCP server** — wrap your own ADK tools behind an MCP server so *any* MCP client (not just ADK) can call them.

**Gemini CLI** also has native MCP support ("MCP Server Integration — extend with custom tools") documented alongside its built-in tools and custom extensions. [google-gemini.github.io/gemini-cli](https://google-gemini.github.io/gemini-cli/)

**Useful off-the-shelf MCP servers for a fast hack:** anything already in this session's environment counts (filesystem, web-fetch/search, GitHub, Slack, database connectors) — the point of `McpToolset` is that you don't have to write a new server, you point ADK at an existing one and move on.

---

## 4. Gemini CLI

**Read this section carefully before assuming your team can just `npm install` free Gemini CLI usage today — the free/individual path was retired.**

### Install
```bash
npm install -g @google/gemini-cli       # or: npx @google/gemini-cli
gemini                                   # then choose "Sign in with Google" for OAuth
```
Requires Node 18+ (Node 20+ recommended in practice). [github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)

### The free-tier reality as of today (2026-08-22)
On **2026-05-19**, Google announced Antigravity CLI and said that on **2026-06-18**, Gemini CLI and the Gemini Code Assist IDE extensions would **stop serving requests** for: Google AI Pro/Ultra subscribers, and anyone using it free via Gemini Code Assist for individuals. Gemini Code Assist for GitHub stopped accepting new org installs the same day. **That cutoff has already passed as of today.** [developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)

Gemini CLI keeps working *only* for: enterprise Code Assist Standard/Enterprise license holders, Gemini Code Assist for GitHub via Google Cloud (existing installs), and anyone using a **paid** Gemini API key or Gemini Enterprise Agent Platform API key. [same source]

Quota table for when Gemini CLI *does* work (requests/user/day):

| Auth method | Tier | Max requests/day |
|---|---|---|
| Google account | Gemini Code Assist (Individual) | 1,000 |
| Google account | Google AI Pro | 1,500 |
| Google account | Google AI Ultra | 2,000 |
| Gemini API key | Free tier (unpaid) | 250 |
| Gemini API key | Pay-as-you-go | Varies |
| Vertex AI | Express mode (free) | Varies |
| Vertex AI | Pay-as-you-go | Varies |

[geminicli.com/docs/resources/quota-and-pricing](https://geminicli.com/docs/resources/quota-and-pricing/)

**Important distinction for this hackathon:** the shutdown is about Gemini CLI/Code Assist as *your team's own coding assistant*. It has nothing to do with calling the Gemini API from ADK/your demo app — that's billed and rate-limited separately (see the API's own free tier at [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing) and [ai.google.dev/gemini-api/docs/rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits)). Don't let CLI confusion make you think the demo itself can't use Gemini for free/cheap — it can, under its own API key quota.

### Extensions / headless / MCP
- Non-interactive scripting: `gemini -p "Explain the architecture of this codebase"`, add `--output-format json` for structured output.
- Built-in tools: file system ops, shell commands, web fetch & search.
- **MCP Server Integration** to add custom tools; **Custom Extensions** to build/share your own commands.
[google-gemini.github.io/gemini-cli](https://google-gemini.github.io/gemini-cli/)

**Verdict:** if your team wants a free terminal coding assistant today, that's now **Antigravity CLI**, not Gemini CLI — see next section. If someone on the team already pays for Gemini API access, Gemini CLI still works and headless mode is genuinely useful for scripted codegen during the build.

---

## 5. Antigravity / Jules / Firebase Studio / AI Studio "Build"

### Antigravity (and Antigravity CLI)
Google's current **agentic development platform** — an IDE plus a terminal-first CLI surface, positioned as the direct successor to free-tier Gemini CLI usage. Antigravity 2.0 is described as "your command center to manage multiple local agents in parallel" — group conversations into Projects, work across multiple workspaces, automate routine tasks with scheduled messages. Antigravity CLI became available to everyone starting 2026-05-19. [antigravity.google](https://antigravity.google/), [antigravity.google/docs/getting-started](https://antigravity.google/docs/getting-started), [developers.googleblog.com — transition post](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)

**For today:** if anyone on the team needs a free agentic coding assistant in the terminal, install Antigravity CLI (download via antigravity.google), not Gemini CLI. It's ~3 months old as a product, so budget a few minutes to get oriented, but it's the tool Google is actively pointing free users toward right now.

### Jules
An **autonomous coding agent** for tasks you hand off and check back on later — bug fixing, version bumps, running tests, small feature building — explicitly framed as async, background work ("Jules does coding tasks you don't want to do"). [jules.google](https://jules.google/)

**Verdict: skip it for this hack.** Jules is designed for asynchronous delegation, not real-time pair-programming under a 5-hour clock — you'd spend more time waiting on a background task than you'd save.

### Google AI Studio "Build" (full-stack vibe coding)
Announced 2026-03-18: AI Studio got an upgraded build experience — a coding agent built from Antigravity's agent harness that turns a single prompt into a full-stack app, with **built-in Firebase integration** and **one-click deploy to Cloud Run**. The first two Firebase-enabled apps are free under the Google Cloud Starter Tier (no payment method required). [blog.google — full-stack vibe coding](https://blog.google/innovation-and-ai/technology/developers-tools/full-stack-vibe-coding-google-ai-studio/), [firebase.blog — AI Studio integration](https://firebase.blog/posts/2026/03/announcing-ai-studio-integration/)

**Verdict: this is a genuinely fast route to a demo-able shell.** For a 5-hour build, prototyping the *frontend/UI* in AI Studio Build and pointing it at an ADK-built agent backend (or vice versa: build the agent logic in ADK, use AI Studio Build to scaffold the UI shell fast) is a legitimate way to buy back an hour. Don't rely on it for the "we built an agent" story alone — a judge asking "what did you build with ADK/A2A/MCP" wants to hear about the agent logic, not just a generated UI.

### Firebase Studio
Being sunset — Google confirmed it remains accessible only until **2027-03-22**. [firebase.blog/posts/2026/05/google-io-2026-announcements](https://firebase.blog/posts/2026/05/google-io-2026-announcements/)

**Verdict: don't start new work here today.** It still technically works, but there's no reason to build fresh hackathon infrastructure on a product Google has already announced is going away, when AI Studio Build is the active replacement path.

---

## 6. Vertex AI Agent Builder / Agent Engine (now "Agent Runtime")

**Naming note:** what used to be marketed as "Vertex AI Agent Builder" / "Agent Engine" is being folded into the rebranded **Gemini Enterprise Agent Platform** (announced at Cloud Next 2026); the ADK docs now call the managed hosting piece **Agent Runtime**. [cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) (redirects to the Agent Runtime docs), [google.github.io/adk-docs/deploy/agent-runtime](https://google.github.io/adk-docs/deploy/agent-runtime/)

It bundles: ADK (open-source, free) as the code-first dev kit, a low-code visual builder, 200+ foundation models, the managed Agent Runtime, persistent memory, and enterprise governance, all pay-as-you-go. The ADK itself costs nothing; what you pay for is the Agent Runtime compute once deployed. Secondary sources (not Google-official, treat as approximate) cite runtime pricing around **$0.0864/vCPU-hour**, memory at **$0.0090/GB-hour**, and session/Memory Bank events at **$0.25 per 1,000 events** — UNVERIFIED against an official Google pricing page, flagging accordingly. [uibakery.io — Vertex AI Agent Builder 2026 guide](https://uibakery.io/blog/vertex-ai-agent-builder), [nerova.ai — Agent Builder pricing 2026](https://nerova.ai/costs-roi/vertex-ai-agent-builder-pricing-explained-2026)

### Verdict: a trap in a 5-hour window
The ADK code you write is portable — the *same* agent runs locally, on Cloud Run, or on Agent Runtime — so there's no code-level reason to deploy to Agent Runtime today. What it costs you is GCP project setup, enabling billing, IAM, and a slower deploy loop, all of which eat directly into a 5-hour clock. **Use `adk deploy cloud_run` if you need a public URL for the demo; skip Agent Runtime unless a mentor specifically asks whether you've thought about production deployment** — in which case, the honest answer is "yes, it's a one-line deploy target since ADK code is portable, we just didn't spend hackathon time on it."

---

## 7. Observability & evaluation (so you can show evidence on stage)

- **`adk web` Trace tab** — every agent session (not just formal evals) gets an interactive trace grouped by user message; click any row for Event / Request / Response / Graph views showing the actual tool-call flow. This is the cheapest way to show a judge "here's what the agent actually did" without extra instrumentation. [google.github.io/adk-docs/evaluate](https://google.github.io/adk-docs/evaluate/)
- **Cloud Trace integration** — if you do deploy to Agent Runtime, there's a dedicated tracing setup guide for query response times and executed operations via Cloud Trace. [cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/tracing](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) (linked from the Agent Runtime overview page)
- **`adk eval`** — CLI runner against an `EvalSet` file (schema defined in [adk-python's `eval_set.py`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py)) for quantitative pass/fail evidence.
- **`pytest` integration** and **`adk conformance`** (baseline-diff regression testing) for anything you want wired into a repeatable check rather than a one-off screenshot. [google.github.io/adk-docs/evaluate](https://google.github.io/adk-docs/evaluate/)

**For a 5-hour hack:** the Trace tab alone is enough "evidence" for a demo — screen-record or screenshot it live. Don't build a formal EvalSet unless the judging rubric explicitly rewards eval rigor; it's real but it's not the fastest points on the clock.

---

## 8. Recommendation

**For a 2–4 person team building in this exact 5-hour window, in priority order:**

1. **Build the agent in ADK (Python).** Fastest install (`pip install google-adk`), most mature docs and examples, `adk web` gives you a working chat UI *and* a debugging trace view for free — that's your dev loop and your demo surface in one. Use `LlmAgent` + one or two `SequentialAgent`/`ParallelAgent` workflow agents if the idea genuinely needs multi-step orchestration; don't force multi-agent structure onto a task that's really one agent with a few tools.
2. **Reach for MCP the moment you need an external tool or data source.** `McpToolset` is a one-line addition — if there's an existing MCP server for what you need (search, a database, a SaaS API), use it instead of writing a custom tool from scratch.
3. **Treat A2A as a stretch goal, not a foundation.** Only build a second A2A-speaking agent once your core single-agent (or single-pipeline) demo already works end to end. If you do it, it's a strong differentiator specifically *because* most teams won't bother — but a half-working A2A handshake demoed live is worse than no A2A at all.
4. **Skip Vertex AI Agent Builder / Agent Runtime deployment.** The GCP project/billing/IAM setup tax isn't worth it in 5 hours; `adk deploy cloud_run` is the pragmatic public-URL option if you need one, and "the same ADK code deploys to Agent Runtime with no changes" is a perfectly good answer if asked.
5. **If you need a fast UI shell**, prototype it in **Google AI Studio Build** (vibe coding + Firebase, one-click Cloud Run deploy) rather than hand-rolling frontend — but keep the actual agent logic in ADK so your technical story holds up under questioning.
6. **Don't rely on free-tier Gemini CLI as your coding assistant** — that path was shut off 2026-06-18. If your team wants an agentic terminal coding tool today, that's **Antigravity CLI**. This is about how *you* write the code, not about what the demo app calls (the demo can still call the Gemini API directly under its own key/quota, independent of this).
7. **Avoid Jules and Firebase Studio entirely for this build** — Jules is async/background by design (wrong shape for a live 5-hour sprint), and Firebase Studio is being sunset with AI Studio Build as its replacement.

**Net:** ADK + `adk web` + MCP is the highest-confidence, lowest-setup-tax path to a working, demoable agent in under 5 hours, with A2A as the one addition worth the risk if time allows and everything else already works.
